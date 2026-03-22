import { Component, ChangeDetectorRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartOptions, Chart } from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';

// Import our new dedicated services
import { TelemetryService } from './core/telemetry.service';
import { AnalyticsService } from './core/analytics.service';

Chart.register(annotationPlugin);

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, BaseChartDirective, HttpClientModule],
  templateUrl: './app.html',
  styleUrls: ['./app.css']
})
export class App {
  @ViewChild('lineChart') lineChart?: BaseChartDirective;
  @ViewChild('barChart') barChart?: BaseChartDirective; 

  isLoading = false;
  fileName = 'No file selected';
  apiData: any = null;
  estimatedRUL: number | string = '--';
  selectedCycleText = 'Click a data point on the line chart to analyze sensors.';

  // --- CHART CONFIGURATIONS ---
  public lineChartData: ChartConfiguration<'line'>['data'] = { datasets: [] };
  public lineChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    onClick: (event, elements) => {
      if (elements.length > 0) this.updateBarChart(elements[0].index);
    },
    elements: { point: { radius: 0, hoverRadius: 8, hitRadius: 15 }, line: { tension: 0.4 } },
    scales: { 
      x: { grid: { display: false }, title: { display: true, text: 'Flight Cycle' } },
      y: { border: { dash: [4, 4] }, title: { display: true, text: 'MSE Error' } }
    },
    plugins: { 
      legend: { position: 'top' },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        callbacks: {
          label: (context) => {
            const value = context.parsed.y || 0;
            const crit = this.apiData?.threshold || 100; 
            const status = value >= crit ? '🔴 CRITICAL' : (value >= crit*0.75 ? '🟡 WARNING' : '🟢 SAFE');
            return `Status: ${status} | Error: ${value.toFixed(5)}`;
          }
        }
      },
      annotation: { annotations: {} }
    }
  };

  public barChartData: ChartConfiguration<'bar'>['data'] = { labels: [], datasets: [] };
  public barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    scales: { x: { grid: { display: false } }, y: { title: { display: true, text: 'Sensor Error Contribution' }, beginAtZero: true } },
    plugins: { legend: { display: false } }
  };

  // Inject our Services
  constructor(
    private telemetryService: TelemetryService,
    private analyticsService: AnalyticsService,
    private cdr: ChangeDetectorRef
  ) {}

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      this.isLoading = true;
      this.fileName = file.name;
      const reader = new FileReader();
      
      reader.onload = (e: any) => {
        // Delegate the network call to the Telemetry Service
        this.telemetryService.analyzeFlightData(e.target.result).subscribe({
          next: (res: any) => {
            this.apiData = res;
            
            // Delegate the math to the Analytics Service
            this.estimatedRUL = this.analyticsService.calculateRUL(res);
            
            // Update the UI
            this.updateLineChart(res);
            this.updateBarChart(res.errors.length - 1);
            this.isLoading = false;
            this.cdr.detectChanges(); 
          },
          error: () => {
            alert("API Error! Ensure uvicorn is running.");
            this.isLoading = false;
            this.cdr.detectChanges();
          }
        });
      };
      reader.readAsText(file);
    }
  }

  // --- UI UPDATE METHODS ---
  updateLineChart(data: any) {
    const threshold = data.threshold;
    this.lineChartOptions.plugins!.annotation!.annotations = {
      dangerLine: {
        type: 'line', yMin: threshold, yMax: threshold,
        borderColor: 'rgb(255, 99, 132)', borderWidth: 2, borderDash: [5, 5],
        label: { display: true, content: 'CRITICAL', position: 'start', backgroundColor: 'red', color: 'white' }
      }
    };

    this.lineChartData = {
      labels: data.cycles,
      datasets: [{
        data: data.errors,
        label: 'Degradation Path',
        borderColor: '#0f172a', 
        fill: true,
        backgroundColor: (context) => {
          const chart = context.chart;
          const {ctx, chartArea} = chart;
          if (!chartArea) return 'rgba(0,0,0,0.1)';
          const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(255, 99, 132, 0.5)'); 
          gradient.addColorStop(1, 'rgba(75, 192, 192, 0.1)'); 
          return gradient;
        }
      }]
    };
    this.lineChart?.update();
  }

  updateBarChart(index: number) {
    if (!this.apiData) return;
    const targetCycle = this.apiData.cycles[index];
    const sensorErrors = this.apiData.all_feature_errors[index];
    
    this.selectedCycleText = `Sensor Diagnostics: Cycle ${targetCycle}`;

    this.barChartData = {
      labels: this.apiData.sensor_names,
      datasets: [{
        data: sensorErrors,
        label: 'Error contribution',
        backgroundColor: sensorErrors.map((v: number) => v > (Math.max(...sensorErrors)*0.8) ? '#ef4444' : '#3b82f6'),
        borderRadius: 5
      }]
    };
    this.barChart?.update();
    this.cdr.detectChanges();
  }
}