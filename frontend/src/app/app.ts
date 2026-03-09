import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  isLoading = false;
  fileName = 'No file selected';
  apiData: any = null;

  public lineChartData: ChartConfiguration<'line'>['data'] = { datasets: [] };
  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    elements: {
      point: { radius: 0 },
      line: { tension: 0.4 }
    },
    scales: { 
      x: { grid: { display: false }, title: { display: true, text: 'Flight Cycle' } },
      y: { border: { dash: [4, 4] }, title: { display: true, text: 'Reconstruction Error (MSE)' } }
    },
    plugins: { legend: { position: 'top' } }
  };

  // ADDED ChangeDetectorRef HERE
  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {}

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.isLoading = true;
      this.fileName = file.name;
      const reader = new FileReader();
      reader.onload = (e: any) => this.processAndUpload(e.target.result);
      reader.readAsText(file);
    }
  }

  processAndUpload(text: string) {
    const lines = text.split('\n');
    const engine1Data: number[][] = [];

    lines.forEach(line => {
      const values = line.trim().split(/\s+/);
      if (values[0] === '1') { 
        engine1Data.push(values.map(v => parseFloat(v)));
      }
    });

    this.http.post('http://127.0.0.1:8000/analyze_engine', { raw_rows: engine1Data })
      .subscribe({
        next: (res: any) => {
          // 1. POPUP ALERT TO PROVE IT WORKED
          alert("Success! Python API returned the analysis."); 
          console.log("RAW DATA FROM FASTAPI:", res);
          
          // 2. UPDATE VARIABLES
          this.apiData = res;
          this.updateChart(res);
          this.isLoading = false;

          // 3. FORCE ANGULAR TO REDRAW THE SCREEN
          this.cdr.detectChanges(); 
        },
        error: (err) => {
          alert("Error connecting to Python API!");
          console.error('API Error:', err);
          this.isLoading = false;
          this.cdr.detectChanges();
        }
      });
  }

  updateChart(data: any) {
    this.lineChartData = {
      labels: data.cycles,
      datasets: [
        {
          data: data.errors,
          label: 'System Degradation',
          borderColor: '#0f172a', 
          borderWidth: 2,
          fill: false
        },
        {
          data: Array(data.cycles.length).fill(data.threshold),
          label: 'Critical Threshold',
          borderColor: '#ef4444', 
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          pointRadius: 0
        }
      ]
    };
  }
}