import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { FilterStateService } from '../../services/filter-state.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css'
})
export class SidebarComponent implements OnInit {
  activeItem = 'not-applied';

  constructor(private filterState: FilterStateService) {}

  ngOnInit() {
    this.filterState.filterMode$.subscribe(mode => {
      if (mode === 'saved') this.activeItem = 'saved';
      else if (mode === 'applied') this.activeItem = 'applied';
      else if (mode === 'not-applied') this.activeItem = 'not-applied';
      else if (mode === 'all') this.activeItem = 'all-jobs';
      else if (mode === 'interested') this.activeItem = 'interested';
      else if (mode === 'not-interested') this.activeItem = 'not-interested';
      else this.activeItem = 'not-applied';
    });
  }

  showAllJobs() {
    this.filterState.setMode('not-applied');
  }

  showApplied() {
    this.filterState.setMode('applied');
  }

  showSaved() {
    this.filterState.setMode('saved');
  }

  showInterested() {
    this.filterState.setFeedbackMode('interested');
  }

  showNotInterested() {
    this.filterState.setFeedbackMode('not-interested');
  }
}
