import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OrchestratorComponent } from './pages/orchestrator/orchestrator.component';
import { PlayGiveawaysComponent } from './components/play-giveaways/play-giveaways.component';

const routes: Routes = [
  {
    path: '',
    component: OrchestratorComponent
  },
  {
    path: 'play',
    component: PlayGiveawaysComponent
  },
  {
    path: 'sorteo/:id',
    component: PlayGiveawaysComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SorteosRoutingModule { }
