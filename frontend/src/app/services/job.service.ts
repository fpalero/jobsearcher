import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Job, MOCK_JOBS } from '../models/job.model';

export interface JobsResponse {
  data: Job[];
  total: number;
  limit: number;
  skip: number;
}

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private apiUrl = '/api/jobs';

  constructor(private http: HttpClient) {}

  getJobs(limit = 100, skip = 0, applicable?: boolean): Observable<JobsResponse> {
    let url = `${this.apiUrl}/?limit=${limit}&skip=${skip}`;
    if (applicable !== undefined) {
      url += `&applicable=${applicable}`;
    }
    return this.http.get<JobsResponse>(url).pipe(
      catchError(() => of({ data: MOCK_JOBS, total: MOCK_JOBS.length, limit, skip }))
    );
  }

  generateTailoredPdf(jobId: string): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/tailored-pdf`, { job_id: jobId }, {
      responseType: 'blob',
    });
  }

  generateCoverLetterPdf(jobId: string): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/cover-letter`, { job_id: jobId }, {
      responseType: 'blob',
    });
  }
}
