package com.example.springboot;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.metrics.Meter;
import io.opentelemetry.exporter.otlp.http.metrics.OtlpHttpMetricExporter;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.export.PeriodicMetricReader;
import io.opentelemetry.sdk.resources.Resource;
import org.springframework.stereotype.Component;

import jakarta.annotation.PostConstruct;
import java.time.Duration;

@Component
public class MetricsExporter {
    
    private OpenTelemetry openTelemetry;
    private LongCounter requestsCounter;
    
    @PostConstruct
    public void init() {
        // Create OTLP HTTP exporter - include full path
        OtlpHttpMetricExporter exporter = OtlpHttpMetricExporter.builder()
                .setEndpoint("http://10.96.182.73:4318/v1/metrics")
                .build();
        
        // Create meter provider with periodic export
        SdkMeterProvider meterProvider = SdkMeterProvider.builder()
                .registerMetricReader(
                    PeriodicMetricReader.builder(exporter)
                        .setInterval(Duration.ofSeconds(10))
                        .build())
                .build();
        
        // Create OpenTelemetry SDK
        openTelemetry = OpenTelemetrySdk.builder()
                .setMeterProvider(meterProvider)
                .build();
        
        // Create meter and counter
        Meter meter = openTelemetry.getMeter("airlines-service");
        requestsCounter = meter.counterBuilder("airlines_requests_total")
                .setDescription("Total requests to airlines service")
                .setUnit("1")
                .build();
        
        System.out.println("Standalone OpenTelemetry metrics initialized - exporting every 10 seconds");
    }
    
    public void incrementRequests(String endpoint) {
        requestsCounter.add(1, Attributes.of(
            AttributeKey.stringKey("endpoint"), endpoint));
    }
}