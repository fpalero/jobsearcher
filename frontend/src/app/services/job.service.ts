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

export interface JobCounts {
  total: number;
  available: number;
  applied: number;
  saved: number;
  interested: number;
  not_interested: number;
}

@Injectable({
  providedIn: 'root'
})
export class JobService {
  private apiUrl = '/api/jobs';

  constructor(private http: HttpClient) {}

  getCounts(): Observable<JobCounts> {
    return this.http.get<JobCounts>(`${this.apiUrl}/counts`).pipe(
      catchError(() => of({ total: 0, available: 0, applied: 0, saved: 0, interested: 0, not_interested: 0 }))
    );
  }

  getJobs(limit = 100, skip = 0, applicable?: boolean, saved?: boolean, applied?: boolean, sources?: string[]): Observable<JobsResponse> {
    let url = `${this.apiUrl}/?limit=${limit}&skip=${skip}`;
    if (applicable !== undefined) {
      url += `&applicable=${applicable}`;
    }
    if (saved !== undefined) {
      url += `&saved=${saved}`;
    }
    if (applied !== undefined) {
      url += `&applied=${applied}`;
    }
    if (sources && sources.length > 0) {
      url += `&sources=${sources.join(',')}`;
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

  saveJob(jobId: string, saved: boolean): Observable<{ jobId: string; saved: boolean }> {
    return this.http.post<{ jobId: string; saved: boolean }>(`${this.apiUrl}/${jobId}/save`, { saved });
  }

  applyJob(jobId: string, applied: boolean): Observable<{ jobId: string; applied: boolean }> {
    return this.http.post<{ jobId: string; applied: boolean }>(`${this.apiUrl}/${jobId}/apply`, { applied });
  }

  submitFeedback(jobId: string, rating: number, reasons: string[] = []): Observable<{ jobId: string; feedback: { rating: number; reasons: string[] } }> {
    return this.http.post<{ jobId: string; feedback: { rating: number; reasons: string[] } }>(`${this.apiUrl}/${jobId}/feedback`, { rating, reasons });
  }
}
