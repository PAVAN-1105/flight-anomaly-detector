import { ApplicationConfig } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideCharts, withDefaultRegisterables } from 'ng2-charts';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(), // Enables talking to your FastAPI backend
    provideCharts(withDefaultRegisterables()) // Registers Chart.js elements
  ]
};