use std::mem;
use crate::basic_function::{reconstruct_vec, reconstruct_subarray};
#[unsafe(no_mangle)]
pub extern "C" fn generate_greedy_planning(
    total_slot: i32, max_hours: i32, slot_minutes: i32,
    subjects: *const f32, subjects_len: i32,
    todo: *const f32, todo_len: i32,
    unavailable: *const f32, unavailable_len: i32,
    unavailable_sub: *const f32, unavailable_sub_len: i32
) -> *const i32 {
    let all_slots: Vec<i32> = (0..total_slot).collect();
    let all_subjects: Vec<f32> = reconstruct_vec(subjects, subjects_len);
    let hours_todo: Vec<f32> = reconstruct_vec(todo, todo_len);
    let max_slot = max_hours as f32 / (slot_minutes / 60) as f32;

    let flat_unavailability = reconstruct_vec(unavailable, unavailable_len);
    let subarray = reconstruct_vec(unavailable_sub, unavailable_sub_len)
        .iter().map(|&x| x as usize).collect::<Vec<usize>>();
    let all_unavailability = reconstruct_subarray(&flat_unavailability, &subarray);

    let mut schedule: Vec<i32> = vec![-1; total_slot as usize];

    for subject_id in all_subjects.iter().map(|&x| x as usize) {
        let nb_slot: f32 = hours_todo[subject_id] / (slot_minutes / 60) as f32;
        let mut count: i32 = 0;

        for slot in all_slots.iter().map(|&x| x as usize) {
            if schedule[slot] != -1 {
                continue;
            }
            if let Some(inner_vec) = all_unavailability.get(subject_id) {
                let slot_unavailable = slot as f32;
                if inner_vec.contains(&slot_unavailable) {
                    continue;
                }
            }
            schedule[slot] = subject_id as i32;
            count += 1;

            if count as f32 >= max_slot {
                break;
            }
            if count as f32 == nb_slot {
                break;
            }
        }
    }
    let ptr= schedule.as_ptr();
    mem::forget(schedule);
    ptr
}

#[unsafe(no_mangle)]
pub extern "C" fn free_greedy_planning(ptr: *const i32) {
    if ptr.is_null() {
        return;
    }
    unsafe {
        let _ = Box::from_raw(ptr as *mut i32);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generate_planning_test() {
        let planning = vec![0, -1, 0, 0, -1, -1, -1];

        let subjects = vec![0.0];
        let todo = vec![4.0];
        let unavailable = vec![vec![1.0]];
        let length: Vec<f32> = unavailable.iter().map(|inner_vec| inner_vec.len() as f32).collect();
        let flat: Vec<f32> = unavailable.into_iter().flatten().collect();

        let data = generate_greedy_planning(7, 3, 90,
                                     subjects.as_ptr(), subjects.len() as i32,
                                     todo.as_ptr(), todo.len() as i32,
                                     flat.as_ptr(), flat.len() as i32,
                                     length.as_ptr(), length.len() as i32);

        let arr_slice = unsafe { std::slice::from_raw_parts(data, 7) };
        let new_planning = arr_slice.iter().map(|&x| x).collect::<Vec<i32>>();
        free_greedy_planning(data);
        assert_eq!(planning, new_planning);
    }
}