import { Component, OnInit } from '@angular/core';
import { FilterStateService } from '../../services/filter-state.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit {
  activeItem = 'all-jobs';

  constructor(private filterState: FilterStateService) {}

  ngOnInit() {
    this.filterState.applicable$.subscribe(val => {
      this.activeItem = val === true ? 'applicable' : 'all-jobs';
    });
  }

  showAllJobs() {
    this.filterState.setApplicable(undefined);
  }

  showApplicable() {
    this.filterState.toggleApplicable();
  }
}
