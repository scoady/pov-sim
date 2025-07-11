package com.example.springboot;

import java.util.Arrays;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;

import io.pyroscope.javaagent.PyroscopeAgent;
import io.pyroscope.javaagent.config.Config;
import io.pyroscope.javaagent.EventType;
import io.pyroscope.http.Format;

import jakarta.annotation.PostConstruct;

@SpringBootApplication
public class Application {

	@PostConstruct
	public void initPyroscope() {
		String pyroscopeServerAddress = System.getenv().getOrDefault("PYROSCOPE_SERVER_ADDRESS", "https://profiles-prod-008.grafana.net");
		String applicationName = System.getenv().getOrDefault("PYROSCOPE_APPLICATION_NAME", "airlines-service");
		String basicAuthUser = System.getenv().getOrDefault("PYROSCOPE_BASIC_AUTH_USER", "1093656");
		String basicAuthPassword = System.getenv("PYROSCOPE_BASIC_AUTH_PASSWORD");
		
		// Set system properties for environment variables
		// not super necessary to do it this way but i find it confusing to have 3 different options available to configure the client
		// and wanted to document another valid way to configure the pyroscope client 
		System.setProperty("pyroscope.application.name", applicationName);
		System.setProperty("pyroscope.server.address", pyroscopeServerAddress);
		System.setProperty("pyroscope.labels", "service_name=airlines-service");
		Config config = new Config.Builder()
			.setApplicationName(applicationName)
			.setProfilingEvent(EventType.ITIMER)
			//.setProfilingEvent(EventType.ALLOC)
			.setFormat(Format.JFR)
			.setServerAddress(pyroscopeServerAddress)
			.setBasicAuthUser(basicAuthUser)
			.setBasicAuthPassword(basicAuthPassword)
			.build();
		
		PyroscopeAgent.start(config);
		
		System.out.println("Pyroscope profiling started for: " + applicationName);
		System.out.println("Pyroscope server address: " + pyroscopeServerAddress);
		System.out.println("Memory allocation profiling enabled: 512k threshold");
		System.out.println("Lock contention profiling enabled: 10ms threshold");
	}

	public static void main(String[] args) {
		SpringApplication.run(Application.class, args);
	}

	@Bean
	public CommandLineRunner commandLineRunner(ApplicationContext ctx) {
		return args -> {

			System.out.println("Let's inspect the beans provided by Spring Boot:");

			String[] beanNames = ctx.getBeanDefinitionNames();
			Arrays.sort(beanNames);
			for (String beanName : beanNames) {
				System.out.println(beanName);
			}

		};
	}

}
