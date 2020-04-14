# Bag Analysis

## Requirements

Use Python 2.7

## Navigate

`/fmcl/localization_status`

```yaml
header:
  seq: 2357667
  stamp:
    secs: 1586466240
    nsecs: 859080339
  frame_id: ''
localization_valid: True
localization_bad: False
mislocalization_cause: ''
delay_mislocalization_time: 30.0
delay_mislocalization_travel: 5.0
legacy_localization_score: 0.442291858129
legacy_localization_mean_score: 0.707680712006
patch_map_score: -1.31935665953
patch_map_travel: 2742.83326072
patch_map_score_min: -1.63
stddev_position: 0.096996682294
stddev_orientation: 0.0221780192784
stddev_travel: 2744.44020139
```

`/fmcl/localization_score`

```yaml
header:
  seq: 2357670
  stamp:
    secs: 1586466240
    nsecs: 859080339
  frame_id: ''
pose:
  position:
    x: -26.5091686249
    y: 8.25257396698
    z: 0.0
  orientation:
    x: 0.0
    y: 0.0
    z: -0.329938150857
    w: 0.944002551166
scores:
  importance: 0.824907920561
  likelihood: 0.824907920561
  clear: 1.0
  dynamic: 1.0
best_possible:
  importance: 1.77050469171
  likelihood: 1.77050469171
  clear: 1.0
  dynamic: 1.0
worst_possible:
  importance: 0.075
  likelihood: 0.075
  clear: 1.0
  dynamic: 1.0
ratio:
  importance: 0.442291858129
  likelihood: 0.442291858129
  clear: 1.0
  dynamic: 1.0
```

`fmcl/pose`

```yaml
header:
  seq: 2357670
  stamp:
    secs: 1586466240
    nsecs: 859080339
  frame_id: ''
pose:
  pose:
    position:
      x: -26.5091686249
      y: 8.25257396698
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: -0.329938150857
      w: 0.944002551166
  covariance: [0.002960541175873165, 0.0009347208515437376, 0.0, 0.0, 0.0, 0.0, 0.0009347208515437376, 0.006447815200170211, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0004918645391128115]
```

`/fmcl/particlecloud`

```yaml
-
position:
    x: -31.6127815247
    y: 23.0928459167
    z: 0.0
orientation:
    x: 0.0
    y: 0.0
    z: 0.422332406044
    w: 0.906441032887
- 
position:
    x: -31.4858016968
    y: 23.1055259705
    z: 0.0
orientation:
    x: 0.0
    y: 0.0
    z: 0.41169410944
    w: 0.911322116852
- repeat...
```
