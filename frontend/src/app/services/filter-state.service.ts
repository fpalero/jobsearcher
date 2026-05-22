import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export type FilterMode = 'all' | 'not-applied' | 'applicable' | 'applied' | 'saved' | 'interested' | 'not-interested';

@Injectable({ providedIn: 'root' })
export class FilterStateService {
  private applicableSubject = new BehaviorSubject<boolean | undefined>(undefined);
  applicable$: Observable<boolean | undefined> = this.applicableSubject.asObservable();

  private modeSubject = new BehaviorSubject<FilterMode>('not-applied');
  filterMode$: Observable<FilterMode> = this.modeSubject.asObservable();

  setApplicable(value: boolean | undefined) {
    this.applicableSubject.next(value);
    if (value === true) this.modeSubject.next('applicable');
    else this.modeSubject.next('all');
  }

  getApplicable(): boolean | undefined {
    return this.applicableSubject.value;
  }

  toggleApplicable() {
    const current = this.applicableSubject.value;
    this.applicableSubject.next(current === true ? undefined : true);
    if (current === true) this.modeSubject.next('all');
    else this.modeSubject.next('applicable');
  }

  setMode(mode: FilterMode) {
    this.modeSubject.next(mode);
    if (mode === 'applicable') this.applicableSubject.next(true);
    else if (mode === 'applied') this.applicableSubject.next(true);
    else this.applicableSubject.next(undefined);
  }

  getMode(): FilterMode {
    return this.modeSubject.value;
  }

  setFeedbackMode(mode: 'interested' | 'not-interested') {
    this.modeSubject.next(mode);
    this.applicableSubject.next(undefined);
  }

  resetToDefault() {
    this.setMode('not-applied');
  }
}
