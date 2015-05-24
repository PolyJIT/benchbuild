#!/bin/bash
echo configuration 1
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 2
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 3
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 4
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 5
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 6
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 7
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 8
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 9
ConfigID=adce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-adce -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 10
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 11
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 12
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 13
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 14
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 15
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 16
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 17
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 18
ConfigID=always_inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-always-inline -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 19
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 20
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 21
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 22
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 23
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 24
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 25
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 26
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 27
ConfigID=argpromotion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-argpromotion -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 28
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 29
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 30
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 31
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 32
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 33
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 34
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 35
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 36
ConfigID=break_crit_edges%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-break-crit-edges -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 37
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 38
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 39
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 40
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 41
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 42
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 43
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 44
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 45
ConfigID=codegenprepare%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-codegenprepare -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 46
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 47
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 48
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 49
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 50
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 51
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 52
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 53
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 54
ConfigID=constmerge%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constmerge -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 55
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 56
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 57
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 58
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 59
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 60
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 61
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 62
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 63
ConfigID=constprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-constprop -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 64
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 65
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 66
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 67
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 68
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 69
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 70
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 71
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 72
ConfigID=functionattrs%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-functionattrs -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 73
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 74
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 75
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 76
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 77
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 78
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 79
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 80
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 81
ConfigID=globalopt%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-globalopt -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 82
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 83
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 84
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 85
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 86
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 87
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 88
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 89
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 90
ConfigID=indvars%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-indvars -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 91
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 92
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 93
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 94
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 95
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 96
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 97
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 98
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 99
ConfigID=inline%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-inline -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 100
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 101
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 102
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 103
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 104
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 105
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 106
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 107
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 108
ConfigID=instcombine%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-instcombine -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 109
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 110
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 111
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 112
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 113
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 114
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 115
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 116
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 117
ConfigID=ipconstprop%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipconstprop -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 118
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 119
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 120
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 121
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 122
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 123
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 124
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 125
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 126
ConfigID=ipsccp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-ipsccp -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 127
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 128
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 129
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 130
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 131
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 132
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 133
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 134
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 135
ConfigID=jump_threading%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-jump-threading -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 136
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 137
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 138
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 139
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 140
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 141
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 142
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 143
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 144
ConfigID=lcssa%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-lcssa -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 145
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 146
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 147
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 148
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 149
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 150
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 151
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 152
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 153
ConfigID=licm%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-licm -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 154
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 155
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 156
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 157
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 158
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 159
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 160
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 161
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 162
ConfigID=loop-deletion%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-deletion -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 163
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 164
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 165
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 166
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 167
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 168
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 169
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 170
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 171
ConfigID=loop_reduce%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-reduce -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 172
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 173
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 174
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 175
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 176
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 177
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 178
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 179
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 180
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size1%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -rotation-max-header-size=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 181
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size100%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -rotation-max-header-size=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 182
ConfigID=loop_rotate%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-rotate -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 183
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 184
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 185
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 186
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 187
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 188
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 189
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 190
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 191
ConfigID=loop_simplify%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-simplify -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 192
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 193
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 194
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 195
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 196
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 197
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 198
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 199
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 200
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold100%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -partial-unrolling-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 201
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 202
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost1%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -small-loop-cost=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 203
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost100%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -small-loop-cost=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 204
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count1%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -unroll-count=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-threshold=50 
##################
echo configuration 205
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count100%;%unroll_threshold50%;%
flags+=-loop-unroll -polly-vectorizer=none -unroll-count=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-threshold=50 
##################
echo configuration 206
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold1%;%
flags+=-loop-unroll -polly-vectorizer=none -unroll-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 
##################
echo configuration 207
ConfigID=loop_unroll%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold100%;%
flags+=-loop-unroll -polly-vectorizer=none -unroll-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 
##################
echo configuration 208
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 209
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 210
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 211
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 212
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 213
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 214
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 215
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 216
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold1%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -loop-unswitch-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 217
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold100%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -loop-unswitch-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 218
ConfigID=loop_unswitch%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-unswitch -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 219
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 220
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 221
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 222
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 223
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 224
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 225
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 226
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 227
ConfigID=mergefunc%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergefunc -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 228
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 229
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 230
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 231
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 232
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 233
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 234
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 235
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 236
ConfigID=mergereturn%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-mergereturn -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 237
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 238
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 239
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 240
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 241
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 242
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 243
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 244
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 245
ConfigID=none%;%partial_inliner%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-partial-inliner -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 246
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 247
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 248
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 249
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 250
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 251
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 252
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 253
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 254
ConfigID=none%;%polly_vectorizer%;%reassociate%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-reassociate -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 255
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 256
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 257
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 258
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 259
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 260
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 261
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 262
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 263
ConfigID=none%;%polly_vectorizer%;%scalarreply%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-scalarrepl -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 264
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 265
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 266
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 267
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 268
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 269
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 270
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 271
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 272
ConfigID=none%;%polly_vectorizer%;%sccp%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-sccp -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 273
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 274
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 275
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 276
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 277
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 278
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 279
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 280
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 281
ConfigID=none%;%polly_vectorizer%;%simplifycfg%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-simplifycfg -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 282
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 283
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 284
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 285
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 286
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 287
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 288
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 289
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 290
ConfigID=loop_vectorizer%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-loop-vectorize -polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 291
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 292
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 293
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 294
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 295
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 296
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 297
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 298
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 299
ConfigID=none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 300
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 301
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 302
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 303
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 304
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 305
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 306
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 307
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 308
ConfigID=polly%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=polly -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 309
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 310
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 311
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 312
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 313
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 314
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 315
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 316
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 317
ConfigID=polly_vectorizer%;%unroll_only%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=unroll-only -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 318
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 319
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 320
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 321
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 322
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 323
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 324
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 325
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 326
ConfigID=bb%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=bb -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 327
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 328
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 329
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 330
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 331
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 332
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 333
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 334
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 335
ConfigID=enable_polly_openmp%;%none%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -enable-polly-openmp -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 336
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 337
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 338
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 339
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 340
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 341
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 342
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 343
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 344
ConfigID=none%;%polly_vectorizer%;%polly-codegen-scev%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-codegen-scev -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 345
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 346
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 347
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 348
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 349
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 350
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 351
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 352
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 353
ConfigID=none%;%polly_delinearize%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-delinearize -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 354
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 355
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 356
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 357
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 358
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 359
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 360
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 361
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 362
ConfigID=none%;%polly_no_tiling%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-no-tiling -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 363
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no polly-opt-max-coefficient=1 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 364
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient1000%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no polly-opt-max-coefficient=1000 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 365
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term1%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -polly-opt-max-constant-term=1 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 366
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term100%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -polly-opt-max-constant-term=100 polly-opt-max-coefficient=500 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 367
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll1%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -force-vector-interleave=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 368
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll100%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -force-vector-interleave=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 369
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -inline-threshold=1 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 370
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold1000%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold0%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -inline-threshold=1000 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -slp-threshold=0 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################
echo configuration 371
ConfigID=none%;%polly_opt_simplify_depsOFF%;%polly_vectorizer%;%force_vector_unroll50%;%inline_treshold225%;%loop_unswitch_threshold50%;%partial_unrolling_threshold0%;%polly_opt_max_coefficient500%;%polly_opt_max_constant_term20%;%rotation_max_header_size16%;%slp_threshold100%;%small_loop_cost20%;%unroll_count50%;%unroll_threshold50%;%
flags+=-polly-vectorizer=none -polly-opt-simplify-deps=no -slp-threshold=100 polly-opt-max-coefficient=500 -polly-opt-max-constant-term=20 -force-vector-interleave=50 -inline-threshold=225 -loop-unswitch-threshold=50 -partial-unrolling-threshold=0 -rotation-max-header-size=16 -small-loop-cost=20 -unroll-count=50 -unroll-threshold=50 
##################

