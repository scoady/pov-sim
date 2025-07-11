package com.example.springboot;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.annotation.CrossOrigin;

@RestController
public class AirlinesController {
	private static String[] airlines = { "AA", "DL", "UA" };
	
	/**
	 * Dummy method to allocate 1MB object for memory profiling
	 */
	private void allocateDummyMemory() {
		// Allocate 1MB byte array to trigger memory allocation profiling
		byte[] dummyAllocation = new byte[1024 * 1024]; // 1MB
		
		// Do something minimal with the array to prevent compiler optimization
		dummyAllocation[0] = 1;
		dummyAllocation[dummyAllocation.length - 1] = 2;
		
		// Let it go out of scope for garbage collection
		System.out.println("Allocated 1MB dummy object for profiling");
	}

	@Operation(summary = "Index", description = "No-op hello world")
	@GetMapping("/")
	public String index() {
		allocateDummyMemory();
		return "Greetings from Spring Boot!";
	}

	@Operation(summary = "Health check", description = "Performs a simple health check")
	@GetMapping("/health")
	public String health() {
		return "Health check passed!";
	}

	@GetMapping("/airlines")
	@Operation(summary = "Get airlines", description = "Fetch a list of airlines")
	public String getUserById(
			@Parameter(description = "Optional flag - set raise to true to raise an exception") 
			@RequestParam(value = "raise", required = false, defaultValue = "false") boolean raise) {
		allocateDummyMemory();
		if (raise) {
			throw new RuntimeException("Exception raised");
		}
		return String.join(", ", airlines);
	}
}
