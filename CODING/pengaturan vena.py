import cv2


def nothing(x):
    pass


def main():
    cap = cv2.VideoCapture(1)

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 180)
    cap.set(cv2.CAP_PROP_CONTRAST, 200)

    if not cap.isOpened():
        print("Error: Tidak dapat membuka kamera")
        return

    cv2.namedWindow('Video')

    cv2.createTrackbar('Brightness', 'Video', 50, 100, nothing)
    cv2.createTrackbar('Contrast', 'Video', 50, 100, nothing)
    cv2.createTrackbar('CLAHE Clip', 'Video', 2, 10, nothing)

    print("Tekan 'q' untuk keluar")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Tidak dapat membaca frame")
            break

        brightness = cv2.getTrackbarPos('Brightness', 'Video')
        contrast = cv2.getTrackbarPos('Contrast', 'Video')
        clahe_clip = cv2.getTrackbarPos('CLAHE Clip', 'Video')

        frame = cv2.convertScaleAbs(
            frame, alpha=contrast/50, beta=brightness-50)

        # Mengubah frame menjadi grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Menerapkan median blur dengan nilai tetap sebelum CLAHE
        median_blur_value = 5  # Nilai tetap untuk median blur (harus ganjil)
        blurred_frame = cv2.medianBlur(gray, median_blur_value)

        # Menerapkan CLAHE
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        clahe_frame = clahe.apply(blurred_frame)

        # Mengubah kembali ke BGR untuk ditampilkan
        clahe_frame = cv2.cvtColor(clahe_frame, cv2.COLOR_GRAY2BGR)

        # Menerapkan Gaussian blur dengan nilai tetap
        # Nilai tetap untuk Gaussian blur (harus ganjil)
        gaussian_blur_value = 7
        clahe_frame = cv2.GaussianBlur(
            clahe_frame, (gaussian_blur_value, gaussian_blur_value), 0)

        cv2.imshow('Video', clahe_frame)
        cv2.imshow('Gambar', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
