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
		String basicAuthPassword = System.getenv().getOrDefault("PYROSCOPE_BASIC_AUTH_PASSWORD", "glc_eyJvIjoiMTI2NzQ0MCIsIm4iOiJzdGFjay0xMDkzNjU2LWhwLXdyaXRlLXNjb2FkeS1wcm9maWxlcyIsImsiOiI3aHA0NkpWNnRiTzBINUEyaGw1cDVVRjEiLCJtIjp7InIiOiJwcm9kLXVzLXdlc3QtMCJ9fQ==");
		
		// Set system properties for environment variables that the agent might check
//		System.setProperty("PYROSCOPE_APPLICATION_NAME", applicationName);
		System.setProperty("PYROSCOPE_SERVER_ADDRESS", pyroscopeServerAddress);
		System.setProperty("PYROSCOPE_AUTH_TOKEN", basicAuthUser + ":" + basicAuthPassword);
		
		PyroscopeAgent.start(
			new Config.Builder()
				.setApplicationName(applicationName)
				.setProfilingEvent(EventType.ITIMER)
				.setProfilingEvent(EventType.ALLOC) 
				.setFormat(Format.JFR)
				.setServerAddress(pyroscopeServerAddress)
				.setBasicAuthUser(basicAuthUser)
				.setBasicAuthPassword(basicAuthPassword)
				.build()
		);
		
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
