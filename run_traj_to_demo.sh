#!/bin/bash
for traj in trajectories/root/ml_claude37__claude-3-7-sonnet-20250219__t-0.00__p-1.00__c-1.50___instances/*/*.traj; do
  echo "Processing $traj"
  sweagent traj-to-demo "$traj"
done
