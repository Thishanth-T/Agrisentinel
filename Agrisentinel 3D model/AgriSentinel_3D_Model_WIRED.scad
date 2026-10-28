// AGRISENTINEL - detailed visual concept model
// Units: mm. Open with OpenSCAD. F5 preview / F6 render.
// Detailed visual concept with routed colour-coded harnesses and rear speaker.
// Components/wiring are illustrative; verify actual dimensions, voltage levels and pinout before fabrication.
$fn = 20;
box_w=150; box_d=118; box_h=92; wall=3; corner_r=8; lid_h=8;
show_internals=true; show_pole=true; show_wiring=true;

module rounded_box(size=[10,10,10], r=2) {
  linear_extrude(height=size[2]) translate([-size[0]/2+r,-size[1]/2+r]) offset(r=r) square([size[0]-2*r,size[1]-2*r]);
}
module screw(x,y,z,r=2) { color([0.72,0.73,0.75]) translate([x,y,z]) cylinder(h=2,r=r); color([0.2,0.2,0.22]) translate([x,y,z+1.8]) cube([r*1.2,.7,.5],center=true); }
module solar_panel() {
  // Panel sits above lid on two angled supports; blue photovoltaic cells visible on top.
  translate([0,0,box_h+lid_h+18]) rotate([18,0,0]) {
    color([0.12,0.13,0.15]) cube([112,82,4],center=true);
    color([0.62,0.66,0.70]) translate([0,0,2.1]) cube([106,76,0.5],center=true);
    for(x=[-42:21:42]) for(y=[-27:18:27]) {
      color([0.035,0.16,0.52]) translate([x,y,2.55]) cube([18,15,0.65],center=true);
      color([0.15,0.32,0.75]) translate([x-4,y+3,2.9]) cube([7,0.5,0.15],center=true);
    }
    // panel frame rails
    color([0.28,0.30,0.32]) for(y=[-39,39]) translate([0,y,-0.3]) cube([116,2,5],center=true);
  }
  // brackets fixed to the top of the enclosure
  color([0.25,0.26,0.28]) for(x=[-36,36]) {
    translate([x,0,box_h+lid_h+5]) cube([4,5,13],center=true);
    translate([x,0,box_h+lid_h+11]) rotate([18,0,0]) cube([4,5,15],center=true);
  }
}
module button() {
  // Button shaft passes through front wall; cap is fully outside.
  translate([42,-box_d/2-1.5,53]) {
    color([0.10,0.10,0.11]) rotate([90,0,0]) cylinder(h=8,r=12,center=true);
    color([0.24,0.25,0.27]) translate([0,-4,0]) rotate([90,0,0]) cylinder(h=5,r=10.3,center=true);
    color([0.80,0.015,0.025]) translate([0,-7,0]) rotate([90,0,0]) cylinder(h=9,r=8.5,center=true);
    color([1,0.20,0.20]) translate([-2,-11,2]) rotate([90,0,0]) cylinder(h=0.8,r=4.8,center=true);
  }
}
module speaker() {
  // Rear-mounted speaker output grille; driver sits just inside the rear wall.
  translate([-31,box_d/2+1,52]) rotate([90,0,0]) {
    color([0.08,0.08,0.09]) cylinder(h=3,r=20,center=true);
    color([0.25,0.26,0.28]) difference(){ cylinder(h=2,r=18,center=true); cylinder(h=3,r=15,center=true); }
    color([0.09,0.10,0.11]) cylinder(h=1.5,r=15,center=true);
    for(a=[0:30:330]) for(r=[5,9,13]) rotate([0,0,a]) translate([r,0,1]) cylinder(h=1.2,r=1.1,center=true);
    color([0.32,0.33,0.35]) cylinder(h=1,r=3,center=true);
  }
}
module antenna() {
  translate([box_w/2+1,19,72]) rotate([0,90,0]) color([0.62,0.47,0.12]) cylinder(h=9,r=5,center=true);
  translate([box_w/2+7,19,72]) color([0.07,0.07,0.08]) cylinder(h=88,r=3.5);
  translate([box_w/2+7,19,72]) color([0.18,0.18,0.19]) cylinder(h=5,r=5);
  for(z=[8:10:78]) translate([box_w/2+7,19,72+z]) color([0.10,0.10,0.11]) cylinder(h=0.6,r=3.6);
}
module esp32_board() {
  // ESP32 dev board: green PCB, metal RF shield, USB connector, chips, pin headers.
  translate([-25,-8,13]) {
    color([0.025,0.34,0.17]) cube([57,28,2],center=true);
    color([0.72,0.74,0.76]) translate([-22,0,2.2]) cube([8,10,4],center=true); // USB connector
    color([0.08,0.08,0.09]) translate([0,0,3.1]) cube([25,18,3],center=true); // RF shield
    color([0.43,0.45,0.47]) translate([0,0,4.8]) cube([20,13,0.5],center=true);
    color([0.06,0.06,0.07]) translate([14,-5,2.6]) cube([8,7,2],center=true);
    color([0.13,0.13,0.14]) translate([-10,-8,2.5]) cube([7,5,1.6],center=true);
    for(x=[-25:5:25]) for(y=[-12,12]) {
      color([0.72,0.55,0.20]) translate([x,y,1]) cylinder(h=2.3,r=1.1);
      color([0.12,0.12,0.13]) translate([x,y,3.1]) cylinder(h=7,r=0.55);
    }
    // status LEDs
    color([0.05,0.85,0.24]) translate([19,7,2.3]) cube([2,1,1],center=true);
  }
}
module bme280_sensor() {
  // Small sensor breakout board, raised away from warm battery/processor.
  translate([-53,30,24]) {
    color([0.02,0.38,0.16]) cube([20,18,2],center=true);
    color([0.08,0.08,0.09]) translate([0,0,2]) cube([7,7,3],center=true);
    color([0.55,0.58,0.60]) translate([0,0,3.7]) cube([4,4,0.5],center=true);
    for(x=[-7,7]) for(y=[-6,6]) color([0.75,0.58,0.20]) translate([x,y,1.2]) cylinder(h=0.8,r=1.2);
  }
}
module sim800l_board() {
  // GSM/GPRS breakout and metal-can radio module.
  translate([37,-8,14]) {
    color([0.02,0.22,0.55]) cube([32,29,2],center=true);
    color([0.70,0.71,0.72]) translate([0,2,3]) cube([21,19,4],center=true);
    color([0.52,0.54,0.56]) translate([0,2,5.1]) cube([16,14,0.5],center=true);
    color([0.08,0.08,0.09]) translate([-10,-9,2.8]) cube([7,5,2],center=true);
    color([0.83,0.72,0.28]) translate([0,-11,2]) cube([11,4,1],center=true); // SIM holder
    color([0.15,0.15,0.16]) translate([0,-11,2.7]) cube([8,2,1],center=true);
    for(x=[-13:4:13]) for(y=[-12,12]) color([0.75,0.58,0.20]) translate([x,y,1]) cylinder(h=2,r=0.8);
  }
}
module battery() {
  // Purple 18650-style lithium-ion cell with positive cap and insulating ring.
  translate([0,31,43]) rotate([0,90,0]) {
    color([0.28,0.08,0.47]) cylinder(h=66,r=10.2,center=true);
    color([0.42,0.20,0.68]) translate([0,0,32.7]) cylinder(h=1,r=8.8,center=true);
    color([0.70,0.71,0.74]) translate([0,0,33.5]) cylinder(h=0.8,r=4.4,center=true);
    color([0.12,0.12,0.14]) translate([0,0,-32.7]) cylinder(h=1,r=8.8,center=true);
    color([0.62,0.62,0.65]) translate([0,0,-33.4]) cylinder(h=0.7,r=4,center=true);
    // wrap bands
    color([0.46,0.31,0.65]) for(x=[-20,20]) translate([0,0,x]) cylinder(h=2,r=10.35,center=true);
  }
}
module solar_charge_controller() {
  translate([5,-35,14]) {
    color([0.04,0.38,0.18]) cube([29,17,2],center=true);
    color([0.12,0.12,0.13]) translate([-7,0,2]) cube([8,7,3],center=true);
    color([0.65,0.66,0.67]) translate([4,0,2]) cube([7,6,2],center=true);
    color([0.83,0.64,0.18]) for(x=[-12,12]) translate([x,0,1.4]) cube([3,8,2],center=true);
  }
}
// Wire harnesses are represented as rounded, routed tubes. Coordinates are in mm.
module wire_path(points, r=0.85) {
  for(i=[0:len(points)-2]) hull() {
    translate(points[i]) sphere(r=r,$fn=8);
    translate(points[i+1]) sphere(r=r,$fn=8);
  }
}
module connector(pos=[0,0,0], size=[4,3,2], c=[0.12,0.12,0.13]) {
  color(c) translate(pos) cube(size,center=true);
  color([0.72,0.57,0.22]) translate([pos[0],pos[1],pos[2]-size[2]/2-0.45]) cube([size[0]*0.55,size[1]*0.55,0.9],center=true);
}
module audio_amp_board() {
  // MAX98357A-style I2S amplifier breakout for a small speaker.
  translate([0,35,14]) {
    color([0.02,0.34,0.17]) cube([25,18,1.8],center=true);
    color([0.08,0.08,0.09]) translate([-3,0,1.8]) cube([8,7,2.4],center=true);
    color([0.72,0.73,0.75]) translate([7,3,1.8]) cube([5,5,1.5],center=true);
    for(x=[-10,-5,0,5,10]) color([0.76,0.59,0.22]) translate([x,-7,0.8]) cylinder(h=1.1,r=0.75);
  }
}
module wiring() {
  // Colour-coded low-voltage harnesses; signal routes are schematic, not a pinout guarantee.
  // Solar panel two-core lead down a support and into the charge controller.
  color([0.88,0.08,0.07]) wire_path([[43,0,111],[43,-5,103],[39,-10,95],[33,-18,88],[27,-25,78],[20,-30,66],[13,-34,48],[7,-35,23]],1.05);
  color([0.08,0.10,0.12]) wire_path([[46,1,110],[46,-4,102],[42,-10,94],[36,-18,86],[30,-25,75],[23,-31,63],[16,-36,46],[10,-36,23]],1.05);
  // Charger to battery protection/terminals.
  color([0.90,0.10,0.08]) wire_path([[7,-28,17],[10,-22,21],[12,-12,28],[12,0,35],[8,18,41],[2,27,43]],1.0);
  color([0.10,0.11,0.13]) wire_path([[10,-29,16],[14,-22,20],[16,-12,27],[16,1,34],[12,19,40],[7,28,43]],1.0);
  // Battery supply to ESP32 and GSM board; SIM800L gets a dedicated heavier supply pair.
  color([0.88,0.08,0.07]) wire_path([[1,25,36],[-5,18,29],[-13,10,20],[-25,4,16]],1.0);
  color([0.10,0.11,0.13]) wire_path([[5,25,35],[0,17,28],[-8,8,19],[-20,2,15]],1.0);
  color([0.88,0.08,0.07]) wire_path([[4,25,35],[18,17,28],[30,8,20],[38,1,16]],1.15);
  color([0.10,0.11,0.13]) wire_path([[8,25,34],[22,17,27],[34,8,19],[43,1,16]],1.15);
  // BME280 I2C + power harness, routed away from the battery for better ambient readings.
  color([0.08,0.34,0.92]) wire_path([[-52,22,24],[-48,16,21],[-43,10,18],[-37,5,16],[-31,3,15]],0.65);
  color([0.10,0.65,0.36]) wire_path([[-54,22,23],[-51,16,20],[-45,10,17],[-39,5,15],[-34,3,15]],0.65);
  color([0.92,0.72,0.08]) wire_path([[-55,22,22],[-52,15,19],[-47,9,16],[-41,4,14],[-37,3,14]],0.65);
  color([0.10,0.11,0.13]) wire_path([[-56,22,21],[-53,15,18],[-49,9,15],[-43,4,13],[-40,3,13]],0.65);
  // ESP32 UART/control lines to SIM800L, with small plug headers shown at both ends.
  color([0.08,0.34,0.92]) wire_path([[-1,-5,16],[8,-4,18],[18,-5,19],[27,-7,18],[34,-8,16]],0.65);
  color([0.88,0.08,0.07]) wire_path([[-1,-8,15],[8,-9,17],[18,-10,18],[27,-11,17],[34,-11,16]],0.65);
  color([0.10,0.65,0.36]) wire_path([[-1,-11,14],[8,-13,16],[18,-14,17],[27,-15,16],[34,-14,15]],0.65);
  color([0.10,0.11,0.13]) wire_path([[-1,-14,13],[8,-17,15],[18,-18,16],[27,-18,15],[34,-17,14]],0.65);
  // External antenna coax: antenna base -> gland -> SIM800L RF connector (not ESP32).
  color([0.06,0.06,0.07]) wire_path([[82,19,72],[77,19,69],[73,19,64],[73,14,58],[72,7,49],[67,0,39],[59,-5,28],[51,-8,20]],1.25);
  color([0.75,0.57,0.20]) translate([82,19,72]) rotate([0,90,0]) cylinder(h=4,r=3.8,center=true);
  // Push-button switch leads pass through the front wall to ESP32 GPIO + GND.
  connector([42,-50,53],[7,5,5]);
  color([0.88,0.08,0.07]) wire_path([[42,-50,53],[39,-44,49],[34,-37,42],[27,-29,34],[16,-22,25],[4,-17,18],[-9,-15,15],[-20,-15,15]],0.75);
  color([0.10,0.11,0.13]) wire_path([[45,-50,51],[43,-43,47],[38,-36,40],[31,-28,32],[20,-21,24],[8,-17,18],[-6,-17,14],[-17,-17,14]],0.75);
  // ESP32 I2S audio -> amplifier; amp output pair -> rear speaker driver.
  color([0.08,0.34,0.92]) wire_path([[-3,0,16],[-2,8,17],[-1,17,17],[0,25,16],[0,31,15]],0.7);
  color([0.10,0.65,0.36]) wire_path([[0,0,15],[2,8,16],[2,17,16],[2,25,15],[2,31,14]],0.7);
  color([0.88,0.08,0.07]) wire_path([[7,38,15],[10,43,20],[13,48,29],[10,53,39],[0,57,47],[-20,58,50],[-31,56,51]],0.9);
  color([0.10,0.11,0.13]) wire_path([[9,38,14],[12,44,19],[15,49,28],[12,54,38],[2,58,46],[-18,59,49],[-31,56,49]],0.9);
  // Visible plug housings make harness endpoints legible in the model.
  connector([-22,-15,15],[7,4,3]); connector([35,-8,15],[6,4,3]);
  connector([-53,22,24],[5,4,3],[0.06,0.23,0.12]); connector([7,38,15],[5,4,3]);
}
module internals() {
  // Standoffs for PCB mounting
  for(p=[[-48,-20],[-2,-20],[-48,4],[-2,4]]) color([0.66,0.67,0.69]) translate([p[0],p[1],7]) cylinder(h=4,r=2.1);
  esp32_board();
  bme280_sensor();
  sim800l_board();
  battery();
  solar_charge_controller();
  audio_amp_board();
  if(show_wiring) wiring();
}
module enclosure() {
  // Hollow main body, with front button/speaker openings and side sensor vents.
  color([0.23,0.25,0.27]) difference() {
    rounded_box([box_w,box_d,box_h],corner_r);
    translate([0,0,wall]) rounded_box([box_w-2*wall,box_d-2*wall,box_h],corner_r-2);
    translate([42,-box_d/2,53]) rotate([90,0,0]) cylinder(h=12,r=8.8,center=true);
    translate([-31,box_d/2,52]) rotate([90,0,0]) cylinder(h=12,r=18,center=true);
    // side air vents near the BME280
    for(z=[20:6:44]) translate([-box_w/2,30,z]) rotate([0,90,0]) cylinder(h=10,r=1.7,center=true);
  }
  // Lid with lip, removable top
  color([0.31,0.33,0.35]) translate([0,0,box_h-1]) difference() {
    rounded_box([box_w+2,box_d+2,8],corner_r);
    translate([0,0,-1]) rounded_box([box_w-2*wall,box_d-2*wall,11],corner_r-2);
  }
  // Lid screws
  for(x=[-65,65]) for(y=[-49,49]) screw(x,y,box_h+5,2.2);
  button(); speaker(); antenna(); solar_panel();
  // Side antenna cable gland and rear speaker grille fixing points.
  color([0.22,0.23,0.25]) translate([box_w/2+0.5,19,72]) rotate([0,90,0]) difference(){ cylinder(h=5,r=6,center=true); cylinder(h=6,r=3.3,center=true); }
  for(x=[-48,-14]) color([0.68,0.69,0.71]) translate([x,box_d/2+1.5,52]) rotate([90,0,0]) cylinder(h=1.2,r=1.2,center=true);
  // Sensor vent cover on left side
  color([0.12,0.13,0.14]) translate([-box_w/2-2,30,30]) rotate([0,90,0]) difference(){ cylinder(h=3,r=12,center=true); cylinder(h=4,r=8.5,center=true); }
  color([0.18,0.19,0.20]) translate([-box_w/2-4,30,30]) rotate([0,90,0]) cylinder(h=2,r=7,center=true);
  // front status LED and nameplate
  color([0.08,0.85,0.30]) translate([17,-box_d/2-1,77]) sphere(r=2.1);
  color([0.07,0.08,0.09]) translate([0,-box_d/2-0.8,18]) cube([66,1.5,12],center=true);
  color([0.92,0.93,0.95]) translate([0,-box_d/2-1.65,18]) rotate([90,0,0]) linear_extrude(height=0.5) text("AGRISENTINEL",size=5.3,halign="center",valign="center",font="Liberation Sans:style=Bold");
  if(show_internals) internals();
}
module pole_mount() {
  // Longer field stand under the box; top of pole touches enclosure underside.
  color([0.14,0.15,0.16]) translate([0,0,-300]) cylinder(h=300,r=17);
  for(z=[-28,-78]) {
    color([0.43,0.44,0.46]) translate([0,0,z]) difference(){ cylinder(h=8,r=23,center=true); cylinder(h=10,r=18,center=true); }
    color([0.48,0.49,0.51]) translate([20,0,z]) cube([10,10,10],center=true);
    color([0.18,0.18,0.19]) translate([25,0,z]) rotate([0,90,0]) cylinder(h=8,r=2.5,center=true);
  }
}
// Assembly
union() { enclosure(); if(show_pole) pole_mount(); }
