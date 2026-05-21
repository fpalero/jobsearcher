import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class FilterStateService {
  private applicableSubject = new BehaviorSubject<boolean | undefined>(undefined);
  applicable$: Observable<boolean | undefined> = this.applicableSubject.asObservable();

  setApplicable(value: boolean | undefined) {
    this.applicableSubject.next(value);
  }

  getApplicable(): boolean | undefined {
    return this.applicableSubject.value;
  }

  toggleApplicable() {
    const current = this.applicableSubject.value;
    this.applicableSubject.next(current === true ? undefined : true);
  }
}
