use serde::Deserialize;

#[derive(Deserialize)]
struct ScheduleInput {
    params: Params,
    pause_lunch: PauseLunch,
    subjects: Vec<Subject>,
    rooms: Vec<Room>,
}

#[derive(Deserialize)]
struct Params {
    class: String,
    slots_per_day: u32,
    days_per_week: u32,
    slot_duration_minutes: u32,
    max_hours_per_week: u32,
}

#[derive(Deserialize)]
struct PauseLunch {
    start: String,
    end: String,
    slot_index: u32,
}

#[derive(Deserialize)]
struct Subject {
    name: String,
    teacher: String,
    hours_todo: f32,
    hours_total: f32,
    unavailable_periods: Vec<u32>,
}

#[derive(Deserialize)]
struct Room {
    name: String,
    capacity: u32,
}