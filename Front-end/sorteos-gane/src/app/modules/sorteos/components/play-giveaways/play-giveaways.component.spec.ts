import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlayGiveawaysComponent } from './play-giveaways.component';

describe('PlayGiveawaysComponent', () => {
  let component: PlayGiveawaysComponent;
  let fixture: ComponentFixture<PlayGiveawaysComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PlayGiveawaysComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PlayGiveawaysComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});