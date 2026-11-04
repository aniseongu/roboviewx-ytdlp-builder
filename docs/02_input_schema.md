# 02. Input schema

## Input file

```text
data/input/confirmed_segments.csv
```

## Columns

```csv
source_id,candidate_id,youtube_url,ytid,creator_name,video_title,label_code,is_intrusion,group,start_sec,end_sec,attribution_text,notes
```

## Example

```csv
source_id,candidate_id,youtube_url,ytid,creator_name,video_title,label_code,is_intrusion,group,start_sec,end_sec,attribution_text,notes
src_001,cand_001,https://www.youtube.com/watch?v=abc123,abc123,ChannelA,Gravel walk sample,INTRUSION_FOOTSTEP,true,intrusion,32.0,42.0,"ChannelA, YouTube URL",confirmed by team
```

## Validation rules

코드는 권한 여부를 검사하지 않는다.

검사하는 것은 기술적인 항목뿐이다.

```text
source_id: required
candidate_id: required
youtube_url: required
ytid: required
label_code: required
group: intrusion / non_intrusion / robot_noise 중 하나 권장
start_sec: numeric >= 0
end_sec: numeric > start_sec
duration_sec: end_sec - start_sec
recommended duration: 5~10 seconds
```

## Output file

```text
data/metadata/dataset_items.csv
```

## Output columns

```csv
dataset_item_id,source_id,candidate_id,file_path,label_code,is_intrusion,group,start_sec,end_sec,duration_sec,human_verified,quality_status,download_status,attribution_text,notes
```
