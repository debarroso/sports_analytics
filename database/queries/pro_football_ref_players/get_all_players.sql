select distinct player from
(
    select player from pro_football_ref_games.receiving_stats_advanced
    union all
    select player from pro_football_ref_games.return_stats
    union all
    select player from pro_football_ref_games.fumble_stats
    union all
    select player from pro_football_ref_games.rushing_stats_basic
    union all
    select player from pro_football_ref_games.rushing_stats_advanced
    union all
    select player from pro_football_ref_games.receiving_stats_basic
    union all
    select player from pro_football_ref_games.defense_stats_advanced
    union all
    select player from pro_football_ref_games.defense_stats_basic
    union all
    select player from pro_football_ref_games.passing_stats_basic
    union all
    select player from pro_football_ref_games.passing_stats_advanced
    union all
    select player from pro_football_ref_games.kicking_stats
) as t;