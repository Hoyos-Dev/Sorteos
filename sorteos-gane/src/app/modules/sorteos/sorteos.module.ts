import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';

import { SorteosRoutingModule } from './sorteos-routing.module';
import { OrchestratorComponent } from './pages/orchestrator/orchestrator.component';
import { RegisterGiveawayComponent } from './components/register-giveaway/register-giveaway.component';
import { ListGiveawaysComponent } from './components/list-giveaways/list-giveaways.component';
import { PlayGiveawaysComponent } from './components/play-giveaways/play-giveaways.component';
import { UploadFileComponent } from './components/upload-file/upload-file.component';
import { InfoGiveawayComponent } from './components/info-giveaway/info-giveaway.component';
import { SettingsGiveawayComponent } from './components/settings-giveaway/settings-giveaway.component';


@NgModule({
  declarations: [
    OrchestratorComponent,
    RegisterGiveawayComponent,
    ListGiveawaysComponent,
    PlayGiveawaysComponent,
    UploadFileComponent,
    InfoGiveawayComponent,
    SettingsGiveawayComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    SorteosRoutingModule,
    MatIconModule
  ]
})
export class SorteosModule { }
