#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

struct PixelRGB {
    char bytes[3];
};

struct PixelRGBA {
    char bytes[4];
};

template <typename Pixel>
std::istream &operator>>(std::istream &s, Pixel &pixel) {
    s.read(pixel.bytes, sizeof(pixel.bytes));
    return s;
}

template <typename Pixel>
int extractScreenImage(std::string procDumpFname, std::string screenImageFname,
                       int screenImageWidth, int screenImageHeight) {
    int screenSize = screenImageWidth * screenImageHeight;
    if (screenImageWidth < screenImageHeight)
        std::swap(screenImageWidth, screenImageHeight);

    auto screenImageFile =
        std::ofstream(screenImageFname, std::ios::binary | std::ios::out);
    if (!(screenImageFile.good() && screenImageFile.is_open()))
        return 1;

    auto procDumpFile =
        std::ifstream(procDumpFname, std::ios::binary | std::ios::in);
    if (!(procDumpFile.good() && procDumpFile.is_open())) {
        screenImageFile.close();
        return 1;
    }
    auto it = std::istream_iterator<Pixel>{procDumpFile},
         end = std::istream_iterator<Pixel>{};
    if (it == end) {
        procDumpFile.close();
        screenImageFile.close();
        return 1;
    }

    int equalPartLength = 1, pixelsWritten = 0;
    bool writingImage = false;

    Pixel prevPixel = *(it++);

    bool prevPixelIsZero = true;
    for (int i = 0; i < sizeof(prevPixel.bytes); ++i)
        if (prevPixel.bytes[i] != '\0')
            prevPixelIsZero = false;

    for (;; ++it) {
        if (writingImage && (it == end || pixelsWritten == screenSize))
            break;

        Pixel pixel = (it == end ? Pixel() : *it);

        if (writingImage) {
            char tmpchr = pixel.bytes[0];
            pixel.bytes[0] = pixel.bytes[2], pixel.bytes[2] = tmpchr;
            // swapping R and B color channels
            if (sizeof(pixel.bytes) == 4)
                pixel.bytes[3] = (char)0xFF; // setting full alpha channel
            screenImageFile.write(pixel.bytes, sizeof(pixel.bytes));
            ++pixelsWritten;
            continue;
        }

        bool notEqual =
            !std::equal(std::begin(pixel.bytes), std::end(pixel.bytes),
                        std::begin(prevPixel.bytes));

        if (it == end || notEqual) {
            // THE MOST IMPORTANT THING (and it's conceptually wrong):
            // image was found if there's equal line with length=screenImageWidth
            // and it's not the line of zeros
            if (equalPartLength == screenImageWidth && !prevPixelIsZero) {
                writingImage = true;
                for (int i = 0; i < screenImageWidth; ++i)
                    screenImageFile.write(prevPixel.bytes,
                                          sizeof(prevPixel.bytes));
                pixelsWritten = screenImageWidth;
            }
            // that was the start of screen image dumping (if it was found)

            equalPartLength = 1, prevPixel = pixel, prevPixelIsZero = true;
            for (int i = 0; i < sizeof(prevPixel.bytes); ++i)
                if (prevPixel.bytes[i] != '\0')
                    prevPixelIsZero = false;
        } else
            ++equalPartLength;

        if (it == end)
            break;
    }

    procDumpFile.close();
    screenImageFile.close();

    return writingImage && pixelsWritten == screenSize;
}

signed main() {
    auto start = std::chrono::system_clock::now();

    int exitCode = extractScreenImage<PixelRGBA>("PROCESS_DUMP_PATH",
                                                 "OUT_FILENAME", 1920, 1200);
    std::cout << "exitCode = " << exitCode << '\n';

    auto end = std::chrono::system_clock::now();
    auto elapsed =
        std::chrono::duration_cast<std::chrono::seconds>(end - start);
    std::cout << elapsed.count() << " seconds" << '\n';

    return exitCode;
}