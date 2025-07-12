use std::mem;
use rand::Rng;
use crate::basic_function::{reconstruct_subarray, reconstruct_vec};

#[unsafe(no_mangle)]
pub extern "C" fn min_conflicts_planning(
    total_slot: i32, slot_minutes: i32,
    subjects: *const f32, subjects_len: i32,
    todo: *const f32, todo_len: i32,
    unavailable: *const f32, unavailable_len: i32,
    unavailable_sub: *const f32, unavailable_sub_len: i32
) -> *const i32{
    // 1. Constructs params
    let all_subjects: Vec<f32> = reconstruct_vec(subjects, subjects_len);
    let hours_todo: Vec<f32> = reconstruct_vec(todo, todo_len);
    let slot_todo: Vec<i32> = hours_todo.iter().map(|&val_hours| {
        let hours_f64 = val_hours as f64;
        let num_slots_f64 = hours_f64 / (slot_minutes / 60) as f64;
        num_slots_f64 as i32
    }).collect();

    let flat_unavailability = reconstruct_vec(unavailable, unavailable_len);
    let subarray = reconstruct_vec(unavailable_sub, unavailable_sub_len)
        .iter().map(|&x| x as usize).collect::<Vec<usize>>();
    let all_unavailability = reconstruct_subarray(&flat_unavailability, &subarray);

    let mut schedule: Vec<i32> = vec![-1; total_slot as usize];

    // 2. Random the schedule
    let mut rng = rand::rng();
    for i in 0..total_slot {
        let random_index = rng.random_range(0..=all_subjects.len());
        schedule[i as usize] =  if random_index == all_subjects.len() { -1 } else {random_index as i32};
    }

    // 3. Recherche
    for _ in 0..1000 {
        // 3.1 count conflict if == 0 then break
        let (conflict_count, conflict_index) = get_conflict(schedule.clone(), all_unavailability.clone(), slot_todo.clone());
        if conflict_count != 0 {
            // Choose a random one, get the best value for slots with fewer conflicts & if equal rand
            let random_index = rng.random_range(0..conflict_count as usize);

            let conflict_pos = conflict_index[random_index];
            let mut chosen_value = schedule[conflict_pos];
            let mut best_value_for_chosen_variable = schedule[random_index];
            let mut min_conflicts_count = conflict_count;
            let mut tied_values = Vec::new(); // Pour gérer les égalités, on choisit aléatoirement parmi elles

            let mut possible_subjects: Vec<i32> =  all_subjects.iter().map(|&s| s as i32).collect();
            possible_subjects.push(-1);

            for subject_index in 0..possible_subjects.len() {

                let temp_subject = possible_subjects[subject_index] as i32;
                let mut new_schedule = schedule.clone();
                new_schedule[conflict_pos] = temp_subject;

                let (new_conflict_count, _) = get_conflict(
                    new_schedule.clone(),
                    all_unavailability.clone(),
                    slot_todo.clone()
                );
                if new_conflict_count < min_conflicts_count {
                    min_conflicts_count = new_conflict_count;
                    best_value_for_chosen_variable = temp_subject;
                    tied_values = vec![best_value_for_chosen_variable];
                }else if new_conflict_count == min_conflicts_count {
                    tied_values.push(temp_subject);
                }
            }
            if tied_values.len() > 0 {
                let random_i = rng.random_range(0..tied_values.len());
                chosen_value = tied_values[random_i];
            }else {
                chosen_value = best_value_for_chosen_variable;
            }

            schedule[conflict_pos] = chosen_value;
        }
    }
    // return schedule
    let ptr= schedule.as_ptr();
    mem::forget(schedule);
    ptr
}

fn get_conflict(schedule: Vec<i32>, unavailable: Vec<Vec<f32>>, todos: Vec<i32>) -> (i32, Vec<usize>) {
    let mut  conflict_count = 0;
    let mut slot_count_subject = vec![0; todos.len()];
    let mut index_conflicts: Vec<usize> = Vec::new();

    for z in 0..schedule.len() {
        // unavailability
        for i in 0..unavailable.len() {
            for j in 0..unavailable[i].len() {
                if z == unavailable[i][j] as usize && schedule[z] == j as i32 {
                    conflict_count += 1;
                    // Get list of conflicted slots
                    if !index_conflicts.contains(&z) {
                        index_conflicts.push(z);
                    }
                }
            }
        }
        // max slot per subjects
        if schedule[z] != -1 {
            slot_count_subject[schedule[z] as usize] += 1;
            // Get list of conflicted slots
            if slot_count_subject[schedule[z] as usize] > todos[schedule[z] as usize] {
                conflict_count += 1;
                // Get list of conflicted slots
                if !index_conflicts.contains(&z) {
                    index_conflicts.push(z);
                }
            }
        }
    }

    (conflict_count, index_conflicts)
}

#[cfg(test)]
mod tests {
    use crate::basic_function::free_planning;
    use super::*;

    #[test]
    fn test_get_conflict() {
        let planning = vec![0, 0, 0, 0, -1, 0, -1];
        let todo = vec![4];
        let unavailable = vec![vec![1.0]];

        let (conflict_count, index_conflicts) = get_conflict(
            planning.clone(),
            unavailable.clone(),
            todo.clone()
        );
        assert_eq!(conflict_count, 2);
        assert_eq!(index_conflicts, vec![1, 5]);
    }

    #[test]
    fn test_generate_min_conflicts() {
        let subjects = vec![0.0];
        let todo = vec![4.0];
        let unavailable = vec![vec![1.0]];
        let length: Vec<f32> = unavailable.iter().map(|inner_vec| inner_vec.len() as f32).collect();
        let flat: Vec<f32> = unavailable.into_iter().flatten().collect();

        let data = min_conflicts_planning(7, 90,
                                            subjects.as_ptr(), subjects.len() as i32,
                                            todo.as_ptr(), todo.len() as i32,
                                            flat.as_ptr(), flat.len() as i32,
                                            length.as_ptr(), length.len() as i32);
        let arr_slice = unsafe { std::slice::from_raw_parts(data, 7) };
        let new_planning = arr_slice.iter().map(|&x| x).collect::<Vec<i32>>();
        let count_zeros_success = new_planning.iter().filter(|&&x| x == 0).count();
        free_planning(data);
        println!("{:#?}", new_planning);
        assert_eq!(new_planning[1], -1, "La valeur à l'index 1 n'est pas 0.");
        assert!(count_zeros_success <= 4, "Le nombre de zéros n'est pas inférieur à 4.");
    }
}