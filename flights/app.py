from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import get_random_int
import os
import logging
import pyroscope
import time

from opentelemetry import trace, metrics, _logs
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# Configure OpenTelemetry
resource = Resource.create({
    "service.name": "flights-service",
    "service.version": "1.0.0",
    "service.namespace": "pov-sim",
    "deployment.environment": os.getenv("ENVIRONMENT", "dev")
})

# Configure exporters
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://10.225.255.227:4317")
otlp_protocol = os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "grpc")

# Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_exporter = OTLPSpanExporter(
    endpoint=otlp_endpoint,
    insecure=True,
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint=otlp_endpoint,
        insecure=True,
    )
)

# Create views to automatically add resource attributes as labels
def create_resource_attribute_view(metric_name):
    return View(
        instrument_name=metric_name,
        attribute_keys=frozenset([
            "service_name",
            "service_version", 
            "service_namespace",
            "deployment_environment"
        ])
    )

# Define views for all custom metrics
views = [
    create_resource_attribute_view("flights_requests_total"),
    create_resource_attribute_view("bookings_total"),
]

metrics.set_meter_provider(MeterProvider(
    resource=resource, 
    metric_readers=[metric_reader],
    views=views
))
meter = metrics.get_meter(__name__)

# Logging
logger_provider = LoggerProvider(resource=resource)
_logs.set_logger_provider(logger_provider)

otlp_log_exporter = OTLPLogExporter(
    endpoint=otlp_endpoint,
    insecure=True,
)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))

# Configure Pyroscope
pyroscope_server_address = os.getenv("PYROSCOPE_SERVER_ADDRESS", "https://profiles-prod-008.grafana.net")
pyroscope_application_name = os.getenv("PYROSCOPE_APPLICATION_NAME", "flights-service")
pyroscope_basic_auth_user = os.getenv("PYROSCOPE_BASIC_AUTH_USER")
pyroscope_basic_auth_password = os.getenv("PYROSCOPE_BASIC_AUTH_PASSWORD")

pyroscope.configure(
    application_name=pyroscope_application_name,
    server_address=pyroscope_server_address,
    basic_auth_username=pyroscope_basic_auth_user,
    basic_auth_password=pyroscope_basic_auth_password,
    sample_rate=100,
    tags={"environment": "production"}
)

print(f"Pyroscope profiling started for: {pyroscope_application_name}")
print(f"Pyroscope server address: {pyroscope_server_address}")

# Set up Python logging to use OTEL with traceID
class TraceFormatter(logging.Formatter):
    def format(self, record):
        trace_id = ""
        span_id = ""
        
        current_span = trace.get_current_span()
        if current_span != trace.INVALID_SPAN:
            trace_id = format(current_span.get_span_context().trace_id, '032x')
            span_id = format(current_span.get_span_context().span_id, '016x')
        
        # Add traceID and spanID to the log record
        record.traceID = trace_id
        record.spanID = span_id
        
        return super().format(record)

# Configure logging with trace context
handler = logging.StreamHandler()
formatter = TraceFormatter('%(asctime)s - %(name)s - %(levelname)s - traceID=%(traceID)s spanID=%(spanID)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Instrument logging to automatically add trace context
LoggingInstrumentor().instrument(set_logging_format=True)

app = Flask(__name__)
Swagger(app)
CORS(app)

# Instrument Flask and requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Custom metrics
flights_counter = meter.create_counter(
    "flights_requests_total",
    description="Total number of flights requests",
    unit="1",
)

bookings_counter = meter.create_counter(
    "bookings_total", 
    description="Total number of flight bookings",
    unit="1",
)

def simulate_processing(airline):
    """
    Simulate processing time for different airlines
    AA (American Airlines) gets special slow processing - 5 second sleep
    """
    if airline == "AA":
        print(f"Processing AA request - sleeping for 5 seconds for CPU profiling")
        time.sleep(5)
    else:
        print(f"Processing {airline} request - normal processing")
    
    return True

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint
    ---
    responses:
      200:
        description: Returns healthy
    """
    return jsonify({"status": "healthy"}), 200

@app.route("/", methods=['GET'])
def home():
    """No-op home endpoint
    ---
    responses:
      200:
        description: Returns ok
    """
    return jsonify({"message": "ok"}), 200

@app.route("/flights/<airline>", methods=["GET"])
def get_flights(airline):
    """Get flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: airline
        in: path
        type: string
        enum: ["AA", "UA", "DL"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Returns a list of flights for the selected airline
    """
    with tracer.start_as_current_span("get_flights") as span:
        # Simulate processing time (AA gets 5 second sleep)
        simulate_processing(airline)
        
        span.set_attribute("airline", airline)
        flights_counter.add(1, {
            "airline": airline,
            "service_name": resource.attributes.get("service.name", ""),
            "service_version": resource.attributes.get("service.version", ""),
            "service_namespace": resource.attributes.get("service.namespace", ""),
            "deployment_environment": resource.attributes.get("deployment.environment", "production")
        })
        logger.info(f"Getting flights for airline: {airline}")
        
        status_code = request.args.get("raise")
        if status_code:
            span.set_attribute("error", True)
            span.set_attribute("error.message", f"Encountered {status_code} error")
            logger.error(f"Error triggered for airline {airline}: {status_code}")
            raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
        
        random_int = get_random_int(100, 999)
        span.set_attribute("flight_count", 1)
        span.set_attribute("flight_number", random_int)
        logger.info(f"Generated flight {random_int} for airline {airline}")
        
        return jsonify({airline: [random_int]}), 200

@app.route("/flight", methods=["POST"])
def book_flight():
    """Book flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: passenger_name
        in: query
        type: string
        enum: ["John Doe", "Jane Doe"]
        required: true
      - name: flight_num
        in: query
        type: string
        enum: ["101", "202", "303", "404", "505", "606"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Booked a flight for the selected passenger and flight_num
    """
    with tracer.start_as_current_span("book_flight") as span:
        passenger_name = request.args.get("passenger_name")
        flight_num = request.args.get("flight_num")
        
        # Simulate processing time for AA flights (5 second sleep)
        # Check if this is an AA flight booking by looking at flight number prefix
        if flight_num and flight_num.startswith("AA"):
            print(f"Processing AA flight booking - sleeping for 5 seconds for CPU profiling")
            time.sleep(5)
        else:
            print(f"Processing flight {flight_num} booking - normal processing")
        
        span.set_attribute("passenger_name", passenger_name)
        span.set_attribute("flight_num", flight_num)
        bookings_counter.add(1, {
            "flight_num": flight_num,
            "service_name": resource.attributes.get("service.name", ""),
            "service_version": resource.attributes.get("service.version", ""),
            "service_namespace": resource.attributes.get("service.namespace", ""),
            "deployment_environment": resource.attributes.get("deployment.environment", "")
        })
        logger.info(f"Booking flight {flight_num} for passenger: {passenger_name}")
        
        status_code = request.args.get("raise")
        if status_code:
            span.set_attribute("error", True)
            span.set_attribute("error.message", f"Encountered {status_code} error")
            logger.error(f"Error triggered for booking flight {flight_num}: {status_code}")
            raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
        
        booking_id = get_random_int(100, 999)
        span.set_attribute("booking_id", booking_id)
        logger.info(f"Successfully booked flight {flight_num} for {passenger_name} with booking ID: {booking_id}")
        
        return jsonify({"passenger_name": passenger_name, "flight_num": flight_num, "booking_id": booking_id}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
