import random
import time
import numpy as np
from collections import Counter
from PIL import Image, ImageDraw


def random_item(lst: list, remove: bool = False) -> str:
    """
    Returns a random item from a list.

    Args:
        lst: The list to select from
        remove: If True, removes the selected item from the list. Default is False.

    Returns:
        A random item from the list

    Raises:
        ValueError: If the list is empty
        IndexError: If remove=True and the list becomes empty
    """
    if not lst:
        raise ValueError("Cannot select from an empty list")

    selected_item = random.choice(lst)

    if remove:
        lst.remove(selected_item)

    return selected_item


def test_randomness(num_trials=1000):
    """
    Tests the randomness of random_item function by running it multiple times
    and tracking the frequency of each item being selected.

    Args:
        num_trials: Number of times to run the test (default: 1000)
    """
    # Create a test list with distinct items
    test_list = ["A", "B", "C", "D", "E"]
    original_list = test_list.copy()

    # Track selections (without removing items)
    selections = []

    print(f"Testing randomness with {num_trials} trials...")
    print(f"Test list: {test_list}\n")

    for _ in range(num_trials):
        # Use a copy of the original list for each trial to keep all items available
        item = random_item(original_list.copy(), remove=False)
        selections.append(item)

    # Count occurrences
    counts = Counter(selections)

    # Calculate expected frequency (should be approximately equal for all items)
    expected_frequency = num_trials / len(test_list)

    print("Results:")
    print("-" * 50)
    print(f"{'Item':<10} {'Count':<10} {'Percentage':<15} {'Expected':<15}")
    print("-" * 50)

    for item in sorted(test_list):
        count = counts.get(item, 0)
        percentage = (count / num_trials) * 100
        expected_percentage = (1 / len(test_list)) * 100
        print(
            f"{item:<10} {count:<10} {percentage:>6.2f}%       {expected_percentage:>6.2f}%"
        )

    print("-" * 50)
    print(f"\nTotal trials: {num_trials}")
    print(f"Expected frequency per item: ~{expected_frequency:.1f}")

    # Calculate variance to assess randomness quality
    counts_list = [counts.get(item, 0) for item in test_list]
    mean_count = sum(counts_list) / len(counts_list)
    variance = sum((x - mean_count) ** 2 for x in counts_list) / len(counts_list)
    std_dev = variance**0.5

    print(f"Standard deviation: {std_dev:.2f}")
    print(f"Variance: {variance:.2f}")

    # Test the remove functionality
    print("\n" + "=" * 50)
    print("Testing remove functionality:")
    print("=" * 50)
    test_list_remove = ["X", "Y", "Z"]
    print(f"Original list: {test_list_remove}")

    for i in range(len(test_list_remove)):
        item = random_item(test_list_remove, remove=True)
        print(f"Selected: {item}, Remaining: {test_list_remove}")

    print(f"Final list (should be empty): {test_list_remove}")


def draw_8k_image(frame_number: int = 0) -> Image.Image:
    """
    Draws an 8K resolution image (7680 x 4320 pixels).

    Args:
        frame_number: Frame number to create variation in the image (default: 0)

    Returns:
        PIL Image object at 8K resolution
    """
    width, height = 7680, 4320

    # Create gradient using numpy for better performance
    y_coords = np.arange(height).reshape(-1, 1)
    r = (((y_coords / height) * 255) % 256).astype(np.uint8)
    g = ((((y_coords + frame_number * 10) / height) * 255) % 256).astype(np.uint8)
    b = ((((y_coords + frame_number * 20) / height) * 255) % 256).astype(np.uint8)

    # Stack channels and repeat across width
    gradient = np.stack([r, g, b], axis=2)
    gradient = np.repeat(gradient, width, axis=1)

    # Convert to PIL Image
    image = Image.fromarray(gradient, mode="RGB")
    draw = ImageDraw.Draw(image)

    # Add some geometric shapes for visual interest
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 4
    draw.ellipse(
        [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ],
        outline=(255, 255, 255),
        width=10,
    )

    return image


def draw_4k_image(frame_number: int = 0) -> Image.Image:
    """
    Draws a 4K resolution image (3840 x 2160 pixels).

    Args:
        frame_number: Frame number to create variation in the image (default: 0)

    Returns:
        PIL Image object at 4K resolution
    """
    width, height = 3840, 2160

    # Create gradient using numpy for better performance
    y_coords = np.arange(height).reshape(-1, 1)
    r = (((y_coords / height) * 255) % 256).astype(np.uint8)
    g = ((((y_coords + frame_number * 10) / height) * 255) % 256).astype(np.uint8)
    b = ((((y_coords + frame_number * 20) / height) * 255) % 256).astype(np.uint8)

    # Stack channels and repeat across width
    gradient = np.stack([r, g, b], axis=2)
    gradient = np.repeat(gradient, width, axis=1)

    # Convert to PIL Image
    image = Image.fromarray(gradient, mode="RGB")
    draw = ImageDraw.Draw(image)

    # Add some geometric shapes for visual interest
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 4
    draw.ellipse(
        [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ],
        outline=(255, 255, 255),
        width=10,
    )

    return image


def draw_1080p_image(frame_number: int = 0) -> Image.Image:
    """
    Draws a 1080p resolution image (1920 x 1080 pixels).

    Args:
        frame_number: Frame number to create variation in the image (default: 0)

    Returns:
        PIL Image object at 1080p resolution
    """
    width, height = 1920, 1080

    # Create gradient using numpy for better performance
    y_coords = np.arange(height).reshape(-1, 1)
    r = (((y_coords / height) * 255) % 256).astype(np.uint8)
    g = ((((y_coords + frame_number * 10) / height) * 255) % 256).astype(np.uint8)
    b = ((((y_coords + frame_number * 20) / height) * 255) % 256).astype(np.uint8)

    # Stack channels and repeat across width
    gradient = np.stack([r, g, b], axis=2)
    gradient = np.repeat(gradient, width, axis=1)

    # Convert to PIL Image
    image = Image.fromarray(gradient, mode="RGB")
    draw = ImageDraw.Draw(image)

    # Add some geometric shapes for visual interest
    center_x, center_y = width // 2, height // 2
    radius = min(width, height) // 4
    draw.ellipse(
        [
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
        ],
        outline=(255, 255, 255),
        width=10,
    )

    return image


def test_image_drawing_performance(num_frames: int = 60):
    """
    Tests the performance of drawing images at different resolutions.
    Measures how long it takes to draw 60 frames at each resolution.

    Args:
        num_frames: Number of frames to draw for each resolution (default: 60)
    """
    resolutions = [
        ("1080p", draw_1080p_image, 1920 * 1080),
        ("4K", draw_4k_image, 3840 * 2160),
        ("8K", draw_8k_image, 7680 * 4320),
    ]

    print(
        f"Testing image drawing performance with {num_frames} frames per resolution..."
    )
    print("=" * 70)
    print()

    results = []

    for resolution_name, draw_func, total_pixels in resolutions:
        print(f"Drawing {num_frames} frames at {resolution_name} resolution...")
        start_time = time.time()

        for frame in range(num_frames):
            image = draw_func(frame)
            # Force image processing to complete
            _ = image.tobytes()

        end_time = time.time()
        elapsed_time = end_time - start_time
        avg_time_per_frame = elapsed_time / num_frames
        pixels_per_second = (total_pixels * num_frames) / elapsed_time

        results.append(
            {
                "resolution": resolution_name,
                "total_time": elapsed_time,
                "avg_per_frame": avg_time_per_frame,
                "pixels_per_second": pixels_per_second,
                "total_pixels": total_pixels,
            }
        )

        print(f"  Total time: {elapsed_time:.2f} seconds")
        print(f"  Average per frame: {avg_time_per_frame:.4f} seconds")
        print(f"  Pixels per second: {pixels_per_second:,.0f}")
        print()

    # Print summary table
    print("=" * 70)
    print("Performance Summary:")
    print("=" * 70)
    print(
        f"{'Resolution':<12} {'Total Time (s)':<18} {'Avg/Frame (s)':<18} {'Pixels/sec':<20}"
    )
    print("-" * 70)

    for result in results:
        print(
            f"{result['resolution']:<12} "
            f"{result['total_time']:>16.2f}  "
            f"{result['avg_per_frame']:>16.4f}  "
            f"{result['pixels_per_second']:>18,.0f}"
        )

    print()

    # Calculate relative performance
    if len(results) >= 2:
        base_time = results[0]["total_time"]
        print("Relative Performance (compared to 1080p):")
        print("-" * 70)
        for result in results:
            ratio = result["total_time"] / base_time
            print(f"{result['resolution']}: {ratio:.2f}x slower than 1080p")


if __name__ == "__main__":
    test_randomness(1000)
    print("\n" + "=" * 70 + "\n")
    test_image_drawing_performance(60)
