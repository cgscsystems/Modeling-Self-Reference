# Wikipedia Raw Downloads + Processed Outputs (Index)
**Last Updated**: 2025-12-31

This document lists **exact file names currently present** in the local workspace under:
- `data/wikipedia/raw/` (downloaded dumps and/or decompressed equivalents)
- `data/wikipedia/processed/` (derived Parquet artifacts)

It also summarizes the **expected outputs** of the extraction pipeline used to produce the processed dataset.

---

## Raw (Downloaded) Files
Directory: `data/wikipedia/raw/`

**Count**: 147 files

### Summary
- Multistream article parts (plain `.xml`): 0
- Multistream article parts (compressed `.bz2`): 70
- SQL dumps present (plain): 3
- SQL dumps present (gz): 3
- Multistream index present (plain): 1
- Multistream index present (bz2): 1

### Full file list
```
.gitkeep
enwiki-20251220-page.sql
enwiki-20251220-page.sql.gz
enwiki-20251220-page_props.sql
enwiki-20251220-page_props.sql.gz
enwiki-20251220-pages-articles-multistream-index.txt
enwiki-20251220-pages-articles-multistream-index.txt.bz2
enwiki-20251220-pages-articles-multistream1.xml-p1p41242
enwiki-20251220-pages-articles-multistream1.xml-p1p41242.bz2
enwiki-20251220-pages-articles-multistream10.xml-p4045403p5399366
enwiki-20251220-pages-articles-multistream10.xml-p4045403p5399366.bz2
enwiki-20251220-pages-articles-multistream11.xml-p5399367p6899366
enwiki-20251220-pages-articles-multistream11.xml-p5399367p6899366.bz2
enwiki-20251220-pages-articles-multistream11.xml-p6899367p7054859
enwiki-20251220-pages-articles-multistream11.xml-p6899367p7054859.bz2
enwiki-20251220-pages-articles-multistream12.xml-p7054860p8554859
enwiki-20251220-pages-articles-multistream12.xml-p7054860p8554859.bz2
enwiki-20251220-pages-articles-multistream12.xml-p8554860p9172788
enwiki-20251220-pages-articles-multistream12.xml-p8554860p9172788.bz2
enwiki-20251220-pages-articles-multistream13.xml-p10672789p11659682
enwiki-20251220-pages-articles-multistream13.xml-p10672789p11659682.bz2
enwiki-20251220-pages-articles-multistream13.xml-p9172789p10672788
enwiki-20251220-pages-articles-multistream13.xml-p9172789p10672788.bz2
enwiki-20251220-pages-articles-multistream14.xml-p11659683p13159682
enwiki-20251220-pages-articles-multistream14.xml-p11659683p13159682.bz2
enwiki-20251220-pages-articles-multistream14.xml-p13159683p14324602
enwiki-20251220-pages-articles-multistream14.xml-p13159683p14324602.bz2
enwiki-20251220-pages-articles-multistream15.xml-p14324603p15824602
enwiki-20251220-pages-articles-multistream15.xml-p14324603p15824602.bz2
enwiki-20251220-pages-articles-multistream15.xml-p15824603p17324602
enwiki-20251220-pages-articles-multistream15.xml-p15824603p17324602.bz2
enwiki-20251220-pages-articles-multistream15.xml-p17324603p17460152
enwiki-20251220-pages-articles-multistream15.xml-p17324603p17460152.bz2
enwiki-20251220-pages-articles-multistream16.xml-p17460153p18960152
enwiki-20251220-pages-articles-multistream16.xml-p17460153p18960152.bz2
enwiki-20251220-pages-articles-multistream16.xml-p18960153p20460152
enwiki-20251220-pages-articles-multistream16.xml-p18960153p20460152.bz2
enwiki-20251220-pages-articles-multistream16.xml-p20460153p20570392
enwiki-20251220-pages-articles-multistream16.xml-p20460153p20570392.bz2
enwiki-20251220-pages-articles-multistream17.xml-p20570393p22070392
enwiki-20251220-pages-articles-multistream17.xml-p20570393p22070392.bz2
enwiki-20251220-pages-articles-multistream17.xml-p22070393p23570392
enwiki-20251220-pages-articles-multistream17.xml-p22070393p23570392.bz2
enwiki-20251220-pages-articles-multistream17.xml-p23570393p23716197
enwiki-20251220-pages-articles-multistream17.xml-p23570393p23716197.bz2
enwiki-20251220-pages-articles-multistream18.xml-p23716198p25216197
enwiki-20251220-pages-articles-multistream18.xml-p23716198p25216197.bz2
enwiki-20251220-pages-articles-multistream18.xml-p25216198p26716197
enwiki-20251220-pages-articles-multistream18.xml-p25216198p26716197.bz2
enwiki-20251220-pages-articles-multistream18.xml-p26716198p27121850
enwiki-20251220-pages-articles-multistream18.xml-p26716198p27121850.bz2
enwiki-20251220-pages-articles-multistream19.xml-p27121851p28621850
enwiki-20251220-pages-articles-multistream19.xml-p27121851p28621850.bz2
enwiki-20251220-pages-articles-multistream19.xml-p28621851p30121850
enwiki-20251220-pages-articles-multistream19.xml-p28621851p30121850.bz2
enwiki-20251220-pages-articles-multistream19.xml-p30121851p31308442
enwiki-20251220-pages-articles-multistream19.xml-p30121851p31308442.bz2
enwiki-20251220-pages-articles-multistream2.xml-p41243p151573
enwiki-20251220-pages-articles-multistream2.xml-p41243p151573.bz2
enwiki-20251220-pages-articles-multistream20.xml-p31308443p32808442
enwiki-20251220-pages-articles-multistream20.xml-p31308443p32808442.bz2
enwiki-20251220-pages-articles-multistream20.xml-p32808443p34308442
enwiki-20251220-pages-articles-multistream20.xml-p32808443p34308442.bz2
enwiki-20251220-pages-articles-multistream20.xml-p34308443p35522432
enwiki-20251220-pages-articles-multistream20.xml-p34308443p35522432.bz2
enwiki-20251220-pages-articles-multistream21.xml-p35522433p37022432
enwiki-20251220-pages-articles-multistream21.xml-p35522433p37022432.bz2
enwiki-20251220-pages-articles-multistream21.xml-p37022433p38522432
enwiki-20251220-pages-articles-multistream21.xml-p37022433p38522432.bz2
enwiki-20251220-pages-articles-multistream21.xml-p38522433p39996245
enwiki-20251220-pages-articles-multistream21.xml-p38522433p39996245.bz2
enwiki-20251220-pages-articles-multistream22.xml-p39996246p41496245
enwiki-20251220-pages-articles-multistream22.xml-p39996246p41496245.bz2
enwiki-20251220-pages-articles-multistream22.xml-p41496246p42996245
enwiki-20251220-pages-articles-multistream22.xml-p41496246p42996245.bz2
enwiki-20251220-pages-articles-multistream22.xml-p42996246p44496245
enwiki-20251220-pages-articles-multistream22.xml-p42996246p44496245.bz2
enwiki-20251220-pages-articles-multistream22.xml-p44496246p44788941
enwiki-20251220-pages-articles-multistream22.xml-p44496246p44788941.bz2
enwiki-20251220-pages-articles-multistream23.xml-p44788942p46288941
enwiki-20251220-pages-articles-multistream23.xml-p44788942p46288941.bz2
enwiki-20251220-pages-articles-multistream23.xml-p46288942p47788941
enwiki-20251220-pages-articles-multistream23.xml-p46288942p47788941.bz2
enwiki-20251220-pages-articles-multistream23.xml-p47788942p49288941
enwiki-20251220-pages-articles-multistream23.xml-p47788942p49288941.bz2
enwiki-20251220-pages-articles-multistream23.xml-p49288942p50564553
enwiki-20251220-pages-articles-multistream23.xml-p49288942p50564553.bz2
enwiki-20251220-pages-articles-multistream24.xml-p50564554p52064553
enwiki-20251220-pages-articles-multistream24.xml-p50564554p52064553.bz2
enwiki-20251220-pages-articles-multistream24.xml-p52064554p53564553
enwiki-20251220-pages-articles-multistream24.xml-p52064554p53564553.bz2
enwiki-20251220-pages-articles-multistream24.xml-p53564554p55064553
enwiki-20251220-pages-articles-multistream24.xml-p53564554p55064553.bz2
enwiki-20251220-pages-articles-multistream24.xml-p55064554p56564553
enwiki-20251220-pages-articles-multistream24.xml-p55064554p56564553.bz2
enwiki-20251220-pages-articles-multistream24.xml-p56564554p57025655
enwiki-20251220-pages-articles-multistream24.xml-p56564554p57025655.bz2
enwiki-20251220-pages-articles-multistream25.xml-p57025656p58525655
enwiki-20251220-pages-articles-multistream25.xml-p57025656p58525655.bz2
enwiki-20251220-pages-articles-multistream25.xml-p58525656p60025655
enwiki-20251220-pages-articles-multistream25.xml-p58525656p60025655.bz2
enwiki-20251220-pages-articles-multistream25.xml-p60025656p61525655
enwiki-20251220-pages-articles-multistream25.xml-p60025656p61525655.bz2
enwiki-20251220-pages-articles-multistream25.xml-p61525656p62585850
enwiki-20251220-pages-articles-multistream25.xml-p61525656p62585850.bz2
enwiki-20251220-pages-articles-multistream26.xml-p62585851p63975909
enwiki-20251220-pages-articles-multistream26.xml-p62585851p63975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p63975910p65475909
enwiki-20251220-pages-articles-multistream27.xml-p63975910p65475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p65475910p66975909
enwiki-20251220-pages-articles-multistream27.xml-p65475910p66975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p66975910p68475909
enwiki-20251220-pages-articles-multistream27.xml-p66975910p68475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p68475910p69975909
enwiki-20251220-pages-articles-multistream27.xml-p68475910p69975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p69975910p71475909
enwiki-20251220-pages-articles-multistream27.xml-p69975910p71475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p71475910p72975909
enwiki-20251220-pages-articles-multistream27.xml-p71475910p72975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p72975910p74475909
enwiki-20251220-pages-articles-multistream27.xml-p72975910p74475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p74475910p75975909
enwiki-20251220-pages-articles-multistream27.xml-p74475910p75975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p75975910p77475909
enwiki-20251220-pages-articles-multistream27.xml-p75975910p77475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p77475910p78975909
enwiki-20251220-pages-articles-multistream27.xml-p77475910p78975909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p78975910p80475909
enwiki-20251220-pages-articles-multistream27.xml-p78975910p80475909.bz2
enwiki-20251220-pages-articles-multistream27.xml-p80475910p81895635
enwiki-20251220-pages-articles-multistream27.xml-p80475910p81895635.bz2
enwiki-20251220-pages-articles-multistream3.xml-p151574p311329
enwiki-20251220-pages-articles-multistream3.xml-p151574p311329.bz2
enwiki-20251220-pages-articles-multistream4.xml-p311330p558391
enwiki-20251220-pages-articles-multistream4.xml-p311330p558391.bz2
enwiki-20251220-pages-articles-multistream5.xml-p558392p958045
enwiki-20251220-pages-articles-multistream5.xml-p558392p958045.bz2
enwiki-20251220-pages-articles-multistream6.xml-p958046p1483661
enwiki-20251220-pages-articles-multistream6.xml-p958046p1483661.bz2
enwiki-20251220-pages-articles-multistream7.xml-p1483662p2134111
enwiki-20251220-pages-articles-multistream7.xml-p1483662p2134111.bz2
enwiki-20251220-pages-articles-multistream8.xml-p2134112p2936260
enwiki-20251220-pages-articles-multistream8.xml-p2134112p2936260.bz2
enwiki-20251220-pages-articles-multistream9.xml-p2936261p4045402
enwiki-20251220-pages-articles-multistream9.xml-p2936261p4045402.bz2
enwiki-20251220-redirect.sql
enwiki-20251220-redirect.sql.gz
```

---

## Processed (Derived) Files
Directory: `data/wikipedia/processed/`

**Count**: 9 files

### Full file list
```
.gitkeep
disambig_pages.parquet
links.parquet
links_prose.parquet
links_resolved.parquet
nlink_sequences.parquet
pages.parquet
redirects.parquet
tmp_nlink_sequences.parquet
```

---

## Expected Pipeline Outputs (Processed)
These are the **expected artifacts** after running the Wikipedia decomposition pipeline (see `data-pipeline/wikipedia-decomposition/implementation-guide.md`).

### Required outputs
- `pages.parquet` (from `page.sql*`)
- `redirects.parquet` (from `redirect.sql*`)
- `disambig_pages.parquet` (from `page_props.sql*`)
- `links_prose.parquet` (from multistream article XML parts)
- `nlink_sequences.parquet` (final N-link sequences; depends on the above)

### Optional / legacy (may exist depending on historical runs)
- `links.parquet` (raw link extraction, non-prose; legacy)
- `links_resolved.parquet` (resolved edges without order; legacy)
- `tmp_nlink_sequences.parquet` (intermediate scratch output)

### Notes
- `data/**` contents are gitignored; this index is stored under `data-pipeline/` so it can be versioned.
- The raw directory currently contains both compressed (`.bz2`/`.gz`) and decompressed (`.xml*`/`.sql`) variants.
