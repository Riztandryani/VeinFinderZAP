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
    cv2.createTrackbar('Median Blur', 'Video', 1, 20, nothing)
    cv2.createTrackbar('Gaussian Blur', 'Video', 1, 20, nothing)

    print("Tekan 'q' untuk keluar")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Tidak dapat membaca frame")
            break

        brightness = cv2.getTrackbarPos('Brightness', 'Video')
        contrast = cv2.getTrackbarPos('Contrast', 'Video')
        clahe_clip = cv2.getTrackbarPos('CLAHE Clip', 'Video')
        median_blur = cv2.getTrackbarPos('Median Blur', 'Video')
        gaussian_blur = cv2.getTrackbarPos('Gaussian Blur', 'Video')

        frame = cv2.convertScaleAbs(
            frame, alpha=contrast/50, beta=brightness-50)

        # Mengubah frame menjadi grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Menerapkan CLAHE
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        clahe_frame = clahe.apply(gray)

        # Mengubah kembali ke BGR untuk ditampilkan
        clahe_frame = cv2.cvtColor(clahe_frame, cv2.COLOR_GRAY2BGR)

        # Menerapkan median blur jika nilai trackbar > 0
        if median_blur > 0:
            clahe_frame = cv2.medianBlur(clahe_frame, 2 * median_blur + 1)

        # Menerapkan Gaussian blur jika nilai trackbar > 0
        if gaussian_blur > 0:
            clahe_frame = cv2.GaussianBlur(
                clahe_frame, (2 * gaussian_blur + 1, 2 * gaussian_blur + 1), 0)

        cv2.imshow('Video', clahe_frame)
        cv2.imshow('Gambar', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
