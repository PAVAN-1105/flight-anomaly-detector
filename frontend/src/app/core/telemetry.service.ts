import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class TelemetryService {
  private apiUrl = 'http://127.0.0.1:8000/analyze_engine';

  constructor(private http: HttpClient) {}

  analyzeFlightData(fileText: string): Observable<any> {
    const lines = fileText.split('\n');
    const engineData: number[][] = [];

    // Parse the raw text file into a 2D array
    lines.forEach(line => {
      const values = line.trim().split(/\s+/);
      if (values[0] === '1') { 
        engineData.push(values.map(v => parseFloat(v)));
      }
    });

    // Send the data to the Python backend
    return this.http.post(this.apiUrl, { raw_rows: engineData });
  }
}