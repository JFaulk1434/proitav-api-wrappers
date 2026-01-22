#include <opencv2/opencv.hpp>
#include <chrono>
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <functional>
#include <algorithm>

using namespace cv;
using namespace std;
using namespace std::chrono;

/**
 * Draws an 8K resolution image (7680 x 4320 pixels).
 * 
 * @param frame_number Frame number to create variation in the image
 * @return Mat object at 8K resolution
 */
Mat draw_8k_image(int frame_number = 0) {
    int width = 7680;
    int height = 4320;
    
    Mat image(height, width, CV_8UC3);
    
    // Create gradient pattern using efficient row operations
    for (int y = 0; y < height; y++) {
        uchar r = static_cast<uchar>(static_cast<int>(y * 255.0 / height) % 256);
        uchar g = static_cast<uchar>(static_cast<int>((y + frame_number * 10) * 255.0 / height) % 256);
        uchar b = static_cast<uchar>(static_cast<int>((y + frame_number * 20) * 255.0 / height) % 256);
        
        Vec3b color(b, g, r); // BGR format for OpenCV
        // Fill entire row at once for better performance
        image.row(y).setTo(Scalar(b, g, r));
    }
    
    // Add geometric shapes for visual interest
    Point center(width / 2, height / 2);
    int radius = min(width, height) / 4;
    circle(image, center, radius, Scalar(255, 255, 255), 10);
    
    return image;
}

/**
 * Draws a 4K resolution image (3840 x 2160 pixels).
 * 
 * @param frame_number Frame number to create variation in the image
 * @return Mat object at 4K resolution
 */
Mat draw_4k_image(int frame_number = 0) {
    int width = 3840;
    int height = 2160;
    
    Mat image(height, width, CV_8UC3);
    
    // Create gradient pattern using efficient row operations
    for (int y = 0; y < height; y++) {
        uchar r = static_cast<uchar>(static_cast<int>(y * 255.0 / height) % 256);
        uchar g = static_cast<uchar>(static_cast<int>((y + frame_number * 10) * 255.0 / height) % 256);
        uchar b = static_cast<uchar>(static_cast<int>((y + frame_number * 20) * 255.0 / height) % 256);
        
        Vec3b color(b, g, r); // BGR format for OpenCV
        // Fill entire row at once for better performance
        image.row(y).setTo(Scalar(b, g, r));
    }
    
    // Add geometric shapes for visual interest
    Point center(width / 2, height / 2);
    int radius = min(width, height) / 4;
    circle(image, center, radius, Scalar(255, 255, 255), 10);
    
    return image;
}

/**
 * Draws a 1080p resolution image (1920 x 1080 pixels).
 * 
 * @param frame_number Frame number to create variation in the image
 * @return Mat object at 1080p resolution
 */
Mat draw_1080p_image(int frame_number = 0) {
    int width = 1920;
    int height = 1080;
    
    Mat image(height, width, CV_8UC3);
    
    // Create gradient pattern using efficient row operations
    for (int y = 0; y < height; y++) {
        uchar r = static_cast<uchar>(static_cast<int>(y * 255.0 / height) % 256);
        uchar g = static_cast<uchar>(static_cast<int>((y + frame_number * 10) * 255.0 / height) % 256);
        uchar b = static_cast<uchar>(static_cast<int>((y + frame_number * 20) * 255.0 / height) % 256);
        
        Vec3b color(b, g, r); // BGR format for OpenCV
        // Fill entire row at once for better performance
        image.row(y).setTo(Scalar(b, g, r));
    }
    
    // Add geometric shapes for visual interest
    Point center(width / 2, height / 2);
    int radius = min(width, height) / 4;
    circle(image, center, radius, Scalar(255, 255, 255), 10);
    
    return image;
}

/**
 * Tests the performance of drawing images at different resolutions.
 * Measures how long it takes to draw 60 frames at each resolution.
 * 
 * @param num_frames Number of frames to draw for each resolution (default: 60)
 */
void test_image_drawing_performance(int num_frames = 60) {
    struct ResolutionTest {
        string name;
        function<Mat(int)> draw_func;
        long long total_pixels;
    };
    
    vector<ResolutionTest> resolutions = {
        {"1080p", draw_1080p_image, 1920LL * 1080},
        {"4K", draw_4k_image, 3840LL * 2160},
        {"8K", draw_8k_image, 7680LL * 4320}
    };
    
    cout << "Testing image drawing performance with " << num_frames 
         << " frames per resolution..." << endl;
    cout << string(70, '=') << endl;
    cout << endl;
    
    struct Result {
        double total_time;
        double avg_per_frame;
        double pixels_per_second;
    };
    
    vector<Result> results;
    
    for (auto& res : resolutions) {
        cout << "Drawing " << num_frames << " frames at " << res.name 
             << " resolution..." << endl;
        
        auto start = high_resolution_clock::now();
        
        for (int frame = 0; frame < num_frames; frame++) {
            Mat image = res.draw_func(frame);
            // Force image processing to complete
            (void)image.data;
        }
        
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end - start);
        double elapsed_time = duration.count() / 1000.0;
        double avg_time_per_frame = elapsed_time / num_frames;
        double pixels_per_second = (res.total_pixels * num_frames) / elapsed_time;
        
        Result result;
        result.total_time = elapsed_time;
        result.avg_per_frame = avg_time_per_frame;
        result.pixels_per_second = pixels_per_second;
        results.push_back(result);
        
        cout << "  Total time: " << fixed << setprecision(2) << elapsed_time 
             << " seconds" << endl;
        cout << "  Average per frame: " << setprecision(4) << avg_time_per_frame 
             << " seconds" << endl;
        cout << "  Pixels per second: " << setprecision(0) << pixels_per_second << endl;
        cout << endl;
    }
    
    // Print summary table
    cout << string(70, '=') << endl;
    cout << "Performance Summary:" << endl;
    cout << string(70, '=') << endl;
    cout << left << setw(12) << "Resolution" 
         << right << setw(18) << "Total Time (s)" 
         << setw(18) << "Avg/Frame (s)" 
         << setw(20) << "Pixels/sec" << endl;
    cout << string(70, '-') << endl;
    
    for (size_t i = 0; i < resolutions.size(); i++) {
        cout << left << setw(12) << resolutions[i].name
             << right << setw(16) << fixed << setprecision(2) 
             << results[i].total_time << "  "
             << setw(16) << setprecision(4) << results[i].avg_per_frame << "  "
             << setw(18) << setprecision(0) << results[i].pixels_per_second << endl;
    }
    
    cout << endl;
    
    // Calculate relative performance
    if (results.size() >= 2) {
        double base_time = results[0].total_time;
        cout << "Relative Performance (compared to 1080p):" << endl;
        cout << string(70, '-') << endl;
        for (size_t i = 0; i < resolutions.size(); i++) {
            double ratio = results[i].total_time / base_time;
            cout << resolutions[i].name << ": " << fixed << setprecision(2) 
                 << ratio << "x slower than 1080p" << endl;
        }
    }
}

int main() {
    test_image_drawing_performance(60);
    return 0;
}

