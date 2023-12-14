create table pro_football_ref_parsed.team_stats
(
    game_id             text not null,
    game_date           text,
    team_id             text not null,
    team_name           text,
    team_abbreviation   text,
    team_score          integer,
    coach_id            text,
    coach_name          text,
    home                text,
    result              text,
    first_downs         integer,
    "rush-yds-tds"      text,
    "cmp-att-yd-td-int" text,
    "sacked-yards"      text,
    net_pass_yards      integer,
    total_yards         integer,
    "fumbles-lost"      text,
    turnovers           integer,
    "penalties-yards"   text,
    third_down_conv     text,
    fourth_down_conv    text,
    time_of_possession  text,
    constraint team_stats_pk
        primary key (team_id, game_id)
);

alter table pro_football_ref_parsed.team_stats
    owner to oliver;

create index team_stats_coach_id_index
    on pro_football_ref_parsed.team_stats (coach_id);

create index team_stats_coach_name_index
    on pro_football_ref_parsed.team_stats (coach_name);

create index team_stats_game_date_index
    on pro_football_ref_parsed.team_stats (game_date);

create index team_stats_game_id_index
    on pro_football_ref_parsed.team_stats (game_id);

create index team_stats_home_index
    on pro_football_ref_parsed.team_stats (home);

create index team_stats_result_index
    on pro_football_ref_parsed.team_stats (result);

create index team_stats_team_id_index
    on pro_football_ref_parsed.team_stats (team_id);

create index team_stats_team_name_index
    on pro_football_ref_parsed.team_stats (team_name);

create index team_stats_team_score_index
    on pro_football_ref_parsed.team_stats (team_score);

create index team_stats_team_abbreviation_index
    on pro_football_ref_parsed.team_stats (team_abbreviation);

create table pro_football_ref_parsed.rushing_stats_basic
(
    game_id      text not null,
    game_date    text,
    player       text not null,
    team         text,
    attempts     numeric,
    yards        numeric,
    touchdowns   numeric,
    longest_rush numeric,
    constraint rushing_stats_basic_pk
        primary key (player, game_id)
);

alter table pro_football_ref_parsed.rushing_stats_basic
    owner to oliver;

create index rushing_stats_basic_game_date_index
    on pro_football_ref_parsed.rushing_stats_basic (game_date);

create index rushing_stats_basic_game_id_index
    on pro_football_ref_parsed.rushing_stats_basic (game_id);

create index rushing_stats_basic_player_index
    on pro_football_ref_parsed.rushing_stats_basic (player);

create index rushing_stats_basic_team_index
    on pro_football_ref_parsed.rushing_stats_basic (team);

create table pro_football_ref_parsed.rushing_stats_advanced
(
    game_id                          text not null,
    game_date                        text,
    player                           text not null,
    team                             text,
    attempts                         numeric,
    yards                            numeric,
    touchdowns                       numeric,
    first_downs                      numeric,
    yards_before_contact             numeric,
    yards_before_contact_per_attempt numeric,
    yards_after_contact              numeric,
    yards_after_contact_per_attempt  numeric,
    broken_tackles                   numeric,
    attempts_per_broken_tackle       numeric,
    constraint rushing_stats_advanced_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.rushing_stats_advanced
    owner to oliver;

create index rushing_stats_advanced_game_date_index
    on pro_football_ref_parsed.rushing_stats_advanced (game_date);

create index rushing_stats_advanced_game_id_index
    on pro_football_ref_parsed.rushing_stats_advanced (game_id);

create index rushing_stats_advanced_player_index
    on pro_football_ref_parsed.rushing_stats_advanced (player);

create index rushing_stats_advanced_team_index
    on pro_football_ref_parsed.rushing_stats_advanced (team);

create table pro_football_ref_parsed.return_stats
(
    game_id                text not null,
    game_date              text,
    player                 text not null,
    team                   text,
    kick_returns           numeric,
    kick_return_yards      numeric,
    yards_per_kick_return  numeric,
    kick_return_touchdowns numeric,
    longest_kick_return    numeric,
    punt_returns           numeric,
    punt_return_yards      numeric,
    yards_per_punt_return  numeric,
    punt_return_touchdowns numeric,
    longest_punt_return    numeric,
    constraint return_stats_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.return_stats
    owner to oliver;

create index return_stats_game_date_index
    on pro_football_ref_parsed.return_stats (game_date);

create index return_stats_game_id_index
    on pro_football_ref_parsed.return_stats (game_id);

create index return_stats_player_index
    on pro_football_ref_parsed.return_stats (player);

create index return_stats_team_index
    on pro_football_ref_parsed.return_stats (team);

create table pro_football_ref_parsed.receiving_stats_basic
(
    game_id           text not null,
    game_date         text,
    player            text not null,
    team              text,
    targets           numeric,
    receptions        numeric,
    yards             numeric,
    touchdowns        numeric,
    longest_reception numeric,
    constraint receiving_stats_basic_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.receiving_stats_basic
    owner to oliver;

create index receiving_stats_basic_game_date_index
    on pro_football_ref_parsed.receiving_stats_basic (game_date);

create index receiving_stats_basic_game_id_index
    on pro_football_ref_parsed.receiving_stats_basic (game_id);

create index receiving_stats_basic_player_index
    on pro_football_ref_parsed.receiving_stats_basic (player);

create index receiving_stats_basic_team_index
    on pro_football_ref_parsed.receiving_stats_basic (team);

create table pro_football_ref_parsed.receiving_stats_advanced
(
    game_id                          text not null,
    game_date                        text,
    player                           text not null,
    team                             text,
    targets                          numeric,
    receptions                       numeric,
    yards                            numeric,
    touchdowns                       numeric,
    first_downs                      numeric,
    yards_before_catch               numeric,
    yards_before_catch_per_reception numeric,
    yards_after_catch                numeric,
    yards_after_catch_per_reception  numeric,
    avg_depth_of_target              numeric,
    broken_tackles                   numeric,
    receptions_per_broken_tackle     numeric,
    drops                            numeric,
    drop_percentage                  numeric,
    interceptions_when_targeted      numeric,
    qb_rating_when_targeted          numeric,
    constraint receiving_stats_advanced_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.receiving_stats_advanced
    owner to oliver;

create index receiving_stats_advanced_game_id_index
    on pro_football_ref_parsed.receiving_stats_advanced (game_id);

create index receiving_stats_advanced_player_index
    on pro_football_ref_parsed.receiving_stats_advanced (player);

create index receiving_stats_advanced_game_date_index
    on pro_football_ref_parsed.receiving_stats_advanced (game_date);

create index receiving_stats_advanced_team_index
    on pro_football_ref_parsed.receiving_stats_advanced (team);

create table pro_football_ref_parsed.passing_stats_basic
(
    game_id            text not null,
    game_date          text,
    player             text not null,
    team               text,
    completions        numeric,
    attempts           numeric,
    yards              numeric,
    touchdowns         numeric,
    interceptions      numeric,
    sacked             numeric,
    sacked_yards       numeric,
    longest_completion numeric,
    passer_rating      numeric,
    constraint passing_stats_basic_pk
        primary key (player, game_id)
);

alter table pro_football_ref_parsed.passing_stats_basic
    owner to oliver;

create index passing_stats_basic_game_date_index
    on pro_football_ref_parsed.passing_stats_basic (game_date);

create index passing_stats_basic_game_id_index
    on pro_football_ref_parsed.passing_stats_basic (game_id);

create index passing_stats_basic_player_index
    on pro_football_ref_parsed.passing_stats_basic (player);

create index passing_stats_basic_team_index
    on pro_football_ref_parsed.passing_stats_basic (team);

create table pro_football_ref_parsed.passing_stats_advanced
(
    game_id                            text not null,
    game_date                          text,
    player                             text not null,
    team                               text,
    completions                        numeric,
    attempts                           numeric,
    yards                              numeric,
    first_downs                        numeric,
    first_downs_per_pass_percentage    numeric,
    intended_air_yards                 numeric,
    intended_air_yards_per_pass        numeric,
    completed_air_yards                numeric,
    completed_air_yards_per_completion numeric,
    completed_air_yards_per_attempt    numeric,
    yards_after_catch                  numeric,
    yards_after_catch_per_completion   numeric,
    drops                              numeric,
    drop_percentage_per_attempt        text,
    bad_throws                         numeric,
    bad_throw_percentage               text,
    sacked                             numeric,
    blitzed                            numeric,
    hurried                            numeric,
    hits                               numeric,
    times_pressured                    numeric,
    percent_pressured_per_dropback     text,
    scrambles                          numeric,
    yards_per_scramble                 numeric,
    constraint passing_stats_advanced_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.passing_stats_advanced
    owner to oliver;

create index passing_stats_advanced_game_date_index
    on pro_football_ref_parsed.passing_stats_advanced (game_date);

create index passing_stats_advanced_game_id_index
    on pro_football_ref_parsed.passing_stats_advanced (game_id);

create index passing_stats_advanced_player_index
    on pro_football_ref_parsed.passing_stats_advanced (player);

create index passing_stats_advanced_team_index
    on pro_football_ref_parsed.passing_stats_advanced (team);

create table pro_football_ref_parsed.kicking_stats
(
    game_id                text not null,
    game_date              text,
    player                 text not null,
    team                   text,
    extra_points_made      numeric,
    extra_points_attempted numeric,
    field_goals_made       numeric,
    field_goals_attempted  numeric,
    punts                  numeric,
    punt_yards             numeric,
    yards_per_punt         numeric,
    longest_punt           numeric,
    constraint kicking_stats_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.kicking_stats
    owner to oliver;

create index kicking_stats_game_date_index
    on pro_football_ref_parsed.kicking_stats (game_date);

create index kicking_stats_game_id_index
    on pro_football_ref_parsed.kicking_stats (game_id);

create index kicking_stats_player_index
    on pro_football_ref_parsed.kicking_stats (player);

create index kicking_stats_team_index
    on pro_football_ref_parsed.kicking_stats (team);

create table pro_football_ref_parsed.game_details
(
    game_id        text not null
        constraint game_details_pk
            primary key,
    game_date      text,
    game_time      text,
    won_toss       text,
    roof           text,
    surface        text,
    duration       text,
    attendance     integer,
    weather        text,
    vegas_line     text,
    "over/under"   text,
    referee        text,
    umpire         text,
    down_judge     text,
    line_judge     text,
    back_judge     text,
    side_judge     text,
    field_judge    text,
    head_linesman  text,
    won_ot_toss    text,
    super_bowl_mvp text
);

alter table pro_football_ref_parsed.game_details
    owner to oliver;

create index game_details_back_judge_index
    on pro_football_ref_parsed.game_details (back_judge);

create index game_details_down_judge_index
    on pro_football_ref_parsed.game_details (down_judge);

create index game_details_field_judge_index
    on pro_football_ref_parsed.game_details (field_judge);

create index game_details_game_date_index
    on pro_football_ref_parsed.game_details (game_date);

create index game_details_game_id_index
    on pro_football_ref_parsed.game_details (game_id);

create index game_details_game_time_index
    on pro_football_ref_parsed.game_details (game_time);

create index game_details_head_linesman_index
    on pro_football_ref_parsed.game_details (head_linesman);

create index game_details_line_judge_index
    on pro_football_ref_parsed.game_details (line_judge);

create index "game_details_over/under_index"
    on pro_football_ref_parsed.game_details ("over/under");

create index game_details_referee_index
    on pro_football_ref_parsed.game_details (referee);

create index game_details_roof_index
    on pro_football_ref_parsed.game_details (roof);

create index game_details_side_judge_index
    on pro_football_ref_parsed.game_details (side_judge);

create index game_details_surface_index
    on pro_football_ref_parsed.game_details (surface);

create index game_details_umpire_index
    on pro_football_ref_parsed.game_details (umpire);

create index game_details_vegas_line_index
    on pro_football_ref_parsed.game_details (vegas_line);

create index game_details_weather_index
    on pro_football_ref_parsed.game_details (weather);

create index game_details_won_toss_index
    on pro_football_ref_parsed.game_details (won_toss);

create table pro_football_ref_parsed.fumble_stats
(
    game_id      text not null,
    game_date    text,
    player       text not null,
    team         text,
    fumbles      numeric,
    fumbles_lost numeric,
    constraint fumble_stats_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.fumble_stats
    owner to oliver;

create index fumble_stats_fumbles_index
    on pro_football_ref_parsed.fumble_stats (fumbles);

create index fumble_stats_fumbles_lost_index
    on pro_football_ref_parsed.fumble_stats (fumbles_lost);

create index fumble_stats_game_date_index
    on pro_football_ref_parsed.fumble_stats (game_date);

create index fumble_stats_game_id_index
    on pro_football_ref_parsed.fumble_stats (game_id);

create index fumble_stats_player_index
    on pro_football_ref_parsed.fumble_stats (player);

create index fumble_stats_team_index
    on pro_football_ref_parsed.fumble_stats (team);

create table pro_football_ref_parsed.defense_stats_basic
(
    game_id                              text not null,
    game_date                            text,
    player                               text not null,
    team                                 text,
    interceptions                        numeric,
    interception_return_yards            numeric,
    interceptions_returned_for_touchdown numeric,
    longest_interception_return          numeric,
    passes_defended                      numeric,
    sacks                                numeric,
    tackles_combined                     numeric,
    tackles_solo                         numeric,
    tackles_assisted                     numeric,
    tackles_for_loss                     numeric,
    qb_hits                              numeric,
    fumbles_recovered                    numeric,
    fumble_return_yards                  numeric,
    fumble_rec_touchdown                 numeric,
    forced_fumbles                       numeric,
    constraint defense_stats_basic_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.defense_stats_basic
    owner to oliver;

create index defense_stats_basic_forced_fumbles_index
    on pro_football_ref_parsed.defense_stats_basic (forced_fumbles);

create index defense_stats_basic_game_date_index
    on pro_football_ref_parsed.defense_stats_basic (game_date);

create index defense_stats_basic_game_id_index
    on pro_football_ref_parsed.defense_stats_basic (game_id);

create index defense_stats_basic_interceptions_index
    on pro_football_ref_parsed.defense_stats_basic (interceptions);

create index defense_stats_basic_passes_defended_index
    on pro_football_ref_parsed.defense_stats_basic (passes_defended);

create index defense_stats_basic_player_index
    on pro_football_ref_parsed.defense_stats_basic (player);

create index defense_stats_basic_qb_hits_index
    on pro_football_ref_parsed.defense_stats_basic (qb_hits);

create index defense_stats_basic_sacks_index
    on pro_football_ref_parsed.defense_stats_basic (sacks);

create index defense_stats_basic_tackles_for_loss_index
    on pro_football_ref_parsed.defense_stats_basic (tackles_for_loss);

create index defense_stats_basic_team_index
    on pro_football_ref_parsed.defense_stats_basic (team);

create table pro_football_ref_parsed.defense_stats_advanced
(
    game_id                                text not null,
    game_date                              text not null,
    player                                 text not null,
    team                                   text not null,
    interceptions                          numeric,
    targeted                               numeric,
    completions_when_targeted              numeric,
    completion_percentage_when_targeted    text,
    receiving_yards_allowed                numeric,
    receiving_yards_allowed_per_completion numeric,
    yards_allowed_per_target               numeric,
    receiving_touchdowns_allowed           numeric,
    pass_rating_when_targeted              numeric,
    average_depth_of_target                numeric,
    total_air_yards_on_completions         numeric,
    yards_after_catch_on_completions       numeric,
    blitz                                  numeric,
    qb_hurries                             numeric,
    qb_knockdowns                          numeric,
    sacks                                  numeric,
    pressures                              numeric,
    combined_tackles                       numeric,
    missed_tackles                         numeric,
    missed_tackle_percentage               text,
    constraint defense_stats_advanced_pk
        primary key (game_id, player)
);

alter table pro_football_ref_parsed.defense_stats_advanced
    owner to oliver;

create index defense_stats_advanced_combined_tackles_index
    on pro_football_ref_parsed.defense_stats_advanced (combined_tackles);

create index defense_stats_advanced_game_date_index
    on pro_football_ref_parsed.defense_stats_advanced (game_date);

create index defense_stats_advanced_game_id_index
    on pro_football_ref_parsed.defense_stats_advanced (game_id);

create index defense_stats_advanced_missed_tackles_index
    on pro_football_ref_parsed.defense_stats_advanced (missed_tackles);

create index defense_stats_advanced_player_index
    on pro_football_ref_parsed.defense_stats_advanced (player);

create index defense_stats_advanced_sacks_index
    on pro_football_ref_parsed.defense_stats_advanced (sacks);

create index defense_stats_advanced_targeted_index
    on pro_football_ref_parsed.defense_stats_advanced (targeted);

create index defense_stats_advanced_team_index
    on pro_football_ref_parsed.defense_stats_advanced (team);

