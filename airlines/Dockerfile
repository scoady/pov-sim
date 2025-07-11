# Step 1: Use an official Gradle image to build the application
FROM gradle:8.3.0-jdk17 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project to the container
COPY . .

# Build the application
RUN gradle clean bootJar

# Step 2: Use a lightweight JDK image for running the app
FROM openjdk:17-jdk-slim

# Set the working directory for the runtime container
WORKDIR /app

# Copy the JAR file from the build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Copy the Grafana OpenTelemetry Java agent
COPY grafana-opentelemetry-java.jar /app/grafana-opentelemetry-java.jar

# Expose the port the application runs on
EXPOSE 8080

# Set Pyroscope environment variables
ENV PYROSCOPE_SERVER_ADDRESS=https://profiles-prod-008.grafana.net
ENV PYROSCOPE_APPLICATION_NAME=airlines-service
ENV PYROSCOPE_BASIC_AUTH_USER=1093656
ENV PYROSCOPE_BASIC_AUTH_PASSWORD=glc_eyJvIjoiMTI2NzQ0MCIsIm4iOiJzdGFjay0xMDkzNjU2LWhwLXdyaXRlLXNjb2FkeS1wcm9maWxlcyIsImsiOiI3aFA0NkpWNnRiTzBINUEyaGw1cDVVRjEiLCJtIjp7InIiOiJwcm9kLXVzLXdlc3QtMCJ9fQ==
ENV PYROSCOPE_PROFILER_ALLOC=512k
ENV PYROSCOPE_PROFILER_LOCK=10ms
ENV PYROSCOPE_AUTH_TOKEN=1093656:glc_eyJvIjoiMTI2NzQ0MCIsIm4iOiJzdGFjay0xMDkzNjU2LWhwLXdyaXRlLXNjb2FkeS1wcm9maWxlcyIsImsiOiI3aFA0NkpWNnRiTzBINUEyaGw1cDVVRjEiLCJtIjp7InIiOiJwcm9kLXVzLXdlc3QtMCJ9fQ==

# Set the command to run the application with OpenTelemetry instrumentation
ENTRYPOINT ["java", "-javaagent:/app/grafana-opentelemetry-java.jar", "-jar", "app.jar"]
