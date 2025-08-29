import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ListGiveawaysComponent } from './list-giveaways.component';

describe('ListGiveawaysComponent', () => {
  let component: ListGiveawaysComponent;
  let fixture: ComponentFixture<ListGiveawaysComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ListGiveawaysComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ListGiveawaysComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});