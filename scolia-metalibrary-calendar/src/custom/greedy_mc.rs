use std::cmp::Ordering;
use std::mem;
use crate::basic_function::{reconstruct_subarray, reconstruct_vec};
use crate::heuristics::greedy::greedy_schedule;
use crate::heuristics::min_conflicts::min_conflict_schedule;

#[unsafe(no_mangle)]
pub extern "C" fn generate_greedy_mc_planning(
    total_slot: i32, max_weekly_hours: f32, slot_minutes: i32,
    subjects: *const f32, subjects_len: i32,
    unavailable: *const f32, unavailable_len: i32,
    unavailable_sub: *const f32, unavailable_sub_len: i32,
    hours_done: *const f32, hours_done_len: i32,
    total_hours: *const f32, total_hours_len: i32,
) -> *const i32 {
    // 1. Constructs params

    let max_slot = max_weekly_hours / (slot_minutes / 60) as f32;
    let all_subjects: Vec<f32> = reconstruct_vec(subjects, subjects_len);
    let flat_unavailability = reconstruct_vec(unavailable, unavailable_len);
    let subarray = reconstruct_vec(unavailable_sub, unavailable_sub_len)
        .iter().map(|&x| x as usize).collect::<Vec<usize>>();
    let all_unavailability = reconstruct_subarray(&flat_unavailability, &subarray);
    let hours_done: Vec<f32> = reconstruct_vec(hours_done, hours_done_len);
    let total_hours: Vec<f32> = reconstruct_vec(total_hours, total_hours_len);

    let cap_per_subject = 8.0;

    // GET HOURS TO do for each subjects
    let todos = calculate_weekly_subject_hours(
        &all_subjects,
        &total_hours,
        &hours_done,
        max_weekly_hours,
        cap_per_subject,
    );
    let slot_todo: Vec<i32> = todos.iter().map(|&val_hours| {
        let hours_f64 = val_hours as f64;
        let num_slots_f64 = hours_f64 / (slot_minutes / 60) as f64;
        num_slots_f64 as i32
    }).collect();

    let mut schedule: Vec<i32> = vec![-1; total_slot as usize];

    // 2. Generate Greedy Planning
    schedule = greedy_schedule(
        &all_subjects, &todos,
        slot_minutes, total_slot, max_slot,
        &mut schedule, &all_unavailability);

    // 3. Min conflict
    schedule = min_conflict_schedule(&mut schedule, &all_subjects, &all_unavailability, &slot_todo, 1000);

    // 4. return schedule
     let ptr= schedule.as_ptr();
     mem::forget(schedule);
     ptr
}

pub fn calculate_weekly_subject_hours(
    all_subjects_ids_ordered: &[f32], // Les IDs des matières dans l'ordre de priorité
    total_hours_for_subjects: &[f32],   // Heures totales nécessaires par matière (indexées par position)
    hours_done_for_subjects: &[f32],    // Heures déjà effectuées par matière (indexées par position)
    max_weekly_hours_available: f32, cap_hours_per_subject_week: f32) -> Vec<f32> {
    let subjects_len = all_subjects_ids_ordered.len(); // Nombre total de matières
    if subjects_len == 0 {
        return Vec::new(); // Si aucune matière, retourne un vecteur vide.
    }

    // Initialise le budget total d'heures disponibles pour la semaine.
    let mut hours_remaining_for_week_distribution = max_weekly_hours_available;

    // Ce vecteur contiendra le résultat final : les heures allouées pour chaque matière cette semaine.
    let mut hours_allocated_this_week: Vec<f32> = vec![0.0; subjects_len];

    // --- Phase 1 : Calcul des poids combinés (Priorité 1: Ordre, Priorité 2: Heures totales nécessaires) ---
    let mut weights: Vec<f32> = Vec::with_capacity(subjects_len); // Création d'un nouveau vecteur vide pour les poids
    let mut total_combined_weight = 0.0;

    for i in 0..subjects_len {
        let position_priority_weight: f32 = (subjects_len - i) as f32;
        let hours_needed_weight = total_hours_for_subjects[i];

        let combined_weight = position_priority_weight * hours_needed_weight;
        weights.push(combined_weight);
        total_combined_weight += combined_weight;
    }

    // --- Phase 2 : Allocation proportionnelle initiale des heures ---
    for i in 0..subjects_len {
        let init_hour = if total_combined_weight > 0.0 {
            f32::floor((weights[i] / total_combined_weight) * max_weekly_hours_available)
        } else {
            0.0
        };

        // Assurez-vous que l'allocation initiale ne dépasse pas :
        // 1. Les heures totales restantes à faire pour la matière.
        // 2. Le plafond hebdomadaire par matière.
        let remaining_for_subject_overall = total_hours_for_subjects[i] - hours_done_for_subjects[i];
        let actual_init_hour = init_hour
            .min(remaining_for_subject_overall)
            .min(cap_hours_per_subject_week);

        hours_allocated_this_week[i] += actual_init_hour;
        // Déduit les heures allouées du budget hebdomadaire total.
        hours_remaining_for_week_distribution -= actual_init_hour;
    }

    // --- Phase 3 : Distribution des heures restantes (Priorité 3: Heures déjà faites et ajustements) ---
    // Cette phase va distribuer les heures restantes (souvent des fractions dues à `floor` ou budget non utilisé)
    // en privilégiant les matières qui ont le moins d'heures déjà faites.

    // Liste des matières candidates pour recevoir des heures supplémentaires.
    // Chaque élément est un tuple : (index_matiere, heures_deja_faites_pour_cette_matiere, poids_combiné_original)
    let mut candidates_for_extra_hours: Vec<(usize, f32, f32)> = Vec::new();

    for i in 0..subjects_len {
        let current_allocated = hours_allocated_this_week[i];
        let total_required = total_hours_for_subjects[i];
        let already_done = hours_done_for_subjects[i];

        if (already_done + current_allocated) < total_required &&
            current_allocated < cap_hours_per_subject_week {
            candidates_for_extra_hours.push((i, already_done, weights[i]));
        }
    }

    // Trie les matières candidates selon les priorités suivantes :
    // 1. En premier : celles qui ont le moins d'heures déjà faites (ordre croissant).
    // 2. En second (pour départager les ex-æquo) : celles avec le poids combiné original le plus élevé (ordre décroissant).
    candidates_for_extra_hours.sort_by(|a, b| {
        // Compare d'abord par les heures déjà faites
        if a.1 != b.1 {
            a.1.partial_cmp(&b.1).unwrap_or(Ordering::Equal)
        } else {
            // Si les heures déjà faites sont égales, compare par le poids (priorité d'origine)
            b.2.partial_cmp(&a.2).unwrap_or(Ordering::Equal)
        }
    });

    // Distribue les heures restantes une par une aux candidats, selon l'ordre de tri.
    while hours_remaining_for_week_distribution >= 1.0 && !candidates_for_extra_hours.is_empty() {
        let mut distributed_in_current_round = false; // Indicateur si au moins 1 heure a été distribuée dans ce tour

        let mut i = 0;
        while i < candidates_for_extra_hours.len() && hours_remaining_for_week_distribution >= 1.0 {
            let (subject_idx, _, _) = candidates_for_extra_hours[i];

            let current_allocated = hours_allocated_this_week[subject_idx];
            let total_required = total_hours_for_subjects[subject_idx];
            let already_done = hours_done_for_subjects[subject_idx];

            // Vérifie si on peut ajouter 1 heure à cette matière :
            // 1. Ne dépasse pas le plafond hebdomadaire pour cette matière.
            // 2. Ne dépasse pas le total des heures requises pour la matière (en incluant les heures déjà faites).
            // 3. Nous avons au moins 1 heure restante dans le budget hebdomadaire.
            if current_allocated + 1.0 <= cap_hours_per_subject_week &&
                (already_done + current_allocated + 1.0) <= total_required
            {
                hours_allocated_this_week[subject_idx] += 1.0;
                hours_remaining_for_week_distribution -= 1.0;
                distributed_in_current_round = true; // Oui, une heure a été distribuée

                // Si la matière a atteint son plafond hebdomadaire ou son objectif total d'heures,
                // elle n'a plus besoin d'heures supplémentaires cette semaine, on la retire des candidats.
                if hours_allocated_this_week[subject_idx] >= cap_hours_per_subject_week ||
                    (already_done + hours_allocated_this_week[subject_idx]) >= total_required {
                    candidates_for_extra_hours.remove(i);
                    // Pas d'incrémentation de `i` ici, car l'élément suivant a pris sa place.
                } else {
                    i += 1; // Passe au candidat suivant
                }
            } else {
                i += 1; // Impossible d'ajouter une heure à cette matière, passe au candidat suivant.
            }
        }
        // Condition d'arrêt pour éviter une boucle infinie :
        // Si aucune heure n'a été distribuée dans un tour complet, mais qu'il reste du budget,
        // cela signifie que toutes les matières candidates ne peuvent pas prendre une heure entière (à cause de leurs plafonds individuels ou de leurs objectifs atteints).
        if !distributed_in_current_round && hours_remaining_for_week_distribution > 0.0 {
            break;
        }

        // Si tous les candidats ont été satisfaits ou retirés, sort de la boucle.
        if candidates_for_extra_hours.is_empty() {
            break;
        }
    }

    // return
    hours_allocated_this_week
}

#[cfg(test)]
mod tests {
    use crate::basic_function::free_planning;
    use super::*;

    #[test]
    fn test_calculate_weekly_subject_hours() {
        // Vos matières (ici juste des indices pour l'exemple, leur ordre est la priorité)
        let all_subjects: Vec<f32> = vec![0.0, 1.0, 2.0, 3.0]; // Matière 0 est la plus prioritaire, puis 1, etc.

        // Heures totales nécessaires pour chaque matière (indexées par la position dans `all_subjects`)
        let total_hours_needed: Vec<f32> = vec![
            50.0, // Matière 0
            30.0, // Matière 1
            40.0, // Matière 2
            20.0, // Matière 3
        ];

        // Heures déjà effectuées pour chaque matière (indexées par la position dans `all_subjects`)
        let hours_done: Vec<f32> = vec![
            10.0, // Matière 0 (pas en retard)
            5.0,  // Matière 1 (en retard, < 10)
            25.0, // Matière 2 (pas en retard)
            2.0,  // Matière 3 (en retard, < 10)
        ];

        let max_weekly_hours = 35.0; // Total d'heures disponibles pour la semaine
        let cap_per_subject = 8.0;   // Maximum 8 heures par matière par semaine

        let allocated_hours = calculate_weekly_subject_hours(
            &all_subjects,
            &total_hours_needed,
            &hours_done,
            max_weekly_hours,
            cap_per_subject,
        );

        println!("Heures allouées cette semaine: {:?}", allocated_hours);

        // Assertions pour vérifier les résultats (à adapter selon vos attentes précises)
        // Note: les résultats exacts peuvent varier légèrement en fonction des arrondis.
        // Ici, on vérifie que le total n'est pas dépassé et que la logique de priorité est respectée.
        let total_allocated: f32 = allocated_hours.iter().sum();
        assert!(total_allocated <= max_weekly_hours);
        println!("Total heures allouées: {}", total_allocated);
    }
    #[test]
    fn test_no_subjects() {
        let subjects: Vec<f32> = Vec::new();
        let total_hours: Vec<f32> = Vec::new();
        let done_hours: Vec<f32> = Vec::new();
        let allocated = calculate_weekly_subject_hours(&subjects, &total_hours, &done_hours, 35.0, 8.0);
        assert!(allocated.is_empty());
    }
    #[test]
    fn test_all_hours_done() {
        let subjects: Vec<f32> = vec![0.0];
        let total_hours: Vec<f32> = vec![10.0];
        let done_hours: Vec<f32> = vec![10.0]; // Already done all hours
        let allocated = calculate_weekly_subject_hours(&subjects, &total_hours, &done_hours, 35.0, 8.0);
        assert_eq!(allocated[0], 0.0); // Should allocate 0 hours
    }

    #[test]
    fn test_generate_greedy_mc_planning_simple() {
        // Paramètres
        let expected = vec![0, -1, 0, 0, 0, -1, -1]; // Planning attendu
        let total_slot = 7;
        let slot_minutes = 90;
        let max_weekly_hours = 6.0; // 4 créneaux de 90 min = 6h

        // Une seule matière avec 4h à faire
        let subjects = vec![0.0];
        let total_hours = vec![10.0];
        let hours_done = vec![6.0]; // reste 4h

        // Un créneau d'indisponibilité : le slot 1
        let unavailable = vec![vec![1.0]];
        let flat_unavailable: Vec<f32> = unavailable.clone().into_iter().flatten().collect();
        let unavailable_lengths: Vec<f32> = unavailable.iter().map(|u| u.len() as f32).collect();

        // Appel
        let raw_ptr = generate_greedy_mc_planning(
            total_slot,
            max_weekly_hours,
            slot_minutes,
            subjects.as_ptr(),
            subjects.len() as i32,
            flat_unavailable.as_ptr(),
            flat_unavailable.len() as i32,
            unavailable_lengths.as_ptr(),
            unavailable_lengths.len() as i32,
            hours_done.as_ptr(),
            hours_done.len() as i32,
            total_hours.as_ptr(),
            total_hours.len() as i32
        );

        assert!(!raw_ptr.is_null(), "Le planning retourné est nul");

        let planning: Vec<i32> = unsafe {
            let slice = std::slice::from_raw_parts(raw_ptr, total_slot as usize);
            let result = slice.to_vec();
            free_planning(raw_ptr); // Libère la mémoire manuellement
            result
        };

        println!("Planning généré : {:?}", planning);
        assert_eq!(planning, expected);
    }
}