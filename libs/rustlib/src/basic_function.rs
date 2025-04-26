#[unsafe(no_mangle)]
pub extern "C" fn add(left: u64, right: u64) -> u64 {
    left + right
}

pub fn reconstruct_vec(arr: *const f32, len: i32) -> Vec<f32> {
    let arr_slice = unsafe { std::slice::from_raw_parts(arr, len as usize) };
    let array = arr_slice.iter().map(|&x| x).collect::<Vec<f32>>();
    array
}

pub fn reconstruct_subarray(flat: &[f32], lengths: &[usize]) -> Vec<Vec<f32>> {
    let mut result = Vec::new();
    let mut index = 0;

    for &len in lengths {
        result.push(flat[index..index + len].to_vec());
        index += len;
    }

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn add_test() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }

    #[test]
    fn recompose_test() {
        let input = [1.1, 2.2, 3.3, 4.4];
        let result = reconstruct_vec(input.as_ptr(), 4);
        assert_eq!(result, vec![1.1, 2.2, 3.3, 4.4]);
    }

    #[test]
    fn reconstruct_subarray_test() {
        let flat = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0];
        let lengths = [2, 1, 3];
        let result = reconstruct_subarray(&flat, &lengths);
        assert_eq!(result, vec![vec![1.0, 2.0], vec![3.0], vec![4.0, 5.0, 6.0]]);
    }
}