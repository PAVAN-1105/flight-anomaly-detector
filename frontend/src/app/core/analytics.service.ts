import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  
  // Linear Regression-based RUL Prediction
  calculateRUL(data: any): number | string {
    if (data.first_anomaly_cycle) {
      return 0; // The engine has already failed
    }

    const errors = data.errors;
    const thresh = data.threshold;
    
    // Need at least 5 points to establish a trend
    if (errors.length < 5) return 'Stable'; 

    const y2 = errors[errors.length - 1]; 
    const y1 = errors[errors.length - 5]; 
    const slope = (y2 - y1) / 5;

    // If the error isn't climbing, it's stable
    if (slope <= 0) return 'Stable'; 
    
    // Calculate cycles remaining
    const cyclesLeft = Math.floor((thresh - y2) / slope);
    
    // Cap it for UI safety
    return cyclesLeft > 500 ? '> 500' : (cyclesLeft < 0 ? 0 : cyclesLeft);
  }
}