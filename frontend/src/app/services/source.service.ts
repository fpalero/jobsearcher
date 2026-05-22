import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Source } from '../models/source.model';

@Injectable({ providedIn: 'root' })
export class SourceService {
  private apiUrl = '/api/sources';

  constructor(private http: HttpClient) {}

  getSources(): Observable<{ data: Source[] }> {
    return this.http.get<{ data: Source[] }>(`${this.apiUrl}/`);
  }

  startSync(sourceName: string): Observable<{ source: string; status: string; message: string }> {
    return this.http.post<{ source: string; status: string; message: string }>(`${this.apiUrl}/${sourceName}/sync`, {});
  }

  stopSync(sourceName: string): Observable<{ source: string; status: string; message: string }> {
    return this.http.post<{ source: string; status: string; message: string }>(`${this.apiUrl}/${sourceName}/stop`, {});
  }
}
