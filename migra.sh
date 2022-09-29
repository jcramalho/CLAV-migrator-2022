#!/bin/zsh
cd ontologia
cat clav-base-v5.ttl ti.ttl ent.ttl leg.ttl tip.ttl 100.ttl 150.ttl 200.ttl 250.ttl 300.ttl 350.ttl 400.ttl 450.ttl 500.ttl 550.ttl 600.ttl 650.ttl 700.ttl 710.ttl 750.ttl 800.ttl 850.ttl 900.ttl 950.ttl > clav.ttl 
rapper -c -i turtle clav.ttl 