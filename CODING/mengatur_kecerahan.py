# import cv2

# # Fungsi callback trackbar (diperlukan tetapi tidak digunakan)


# def nothing(x):
#     pass


# def main():
#     # Membuka kamera (0 adalah ID kamera pertama)
#     cap = cv2.VideoCapture(1)

#     # # Mengatur resolusi kamera
#     # cap.set(cv2.CAP_PROP_BRIGHTNESS, 640)
#     # cap.set(cv2.CAP_PROP_CONTRAST, 480)

#     # Mengecek apakah kamera berhasil dibuka
#     if not cap.isOpened():
#         print("Error: Tidak dapat membuka kamera")
#         return

#     # Membuat jendela untuk video
#     cv2.namedWindow('Video')

#     # Membuat trackbar untuk kecerahan dan kontras
#     cv2.createTrackbar('Brightness', 'Video', 50, 100, nothing)
#     cv2.createTrackbar('Contrast', 'Video', 50, 100, nothing)

#     print("Tekan 'q' untuk keluar")

#     while True:
#         # Membaca frame dari kamera
#         ret, frame = cap.read()

#         # Mengecek apakah frame berhasil dibaca
#         if not ret:
#             print("Error: Tidak dapat membaca frame")
#             break

#         # Mendapatkan nilai kecerahan dan kontras dari trackbar
#         brightness = cv2.getTrackbarPos('Brightness', 'Video')
#         contrast = cv2.getTrackbarPos('Contrast', 'Video')

#         # Mengatur kecerahan dan kontras
#         frame = cv2.convertScaleAbs(
#             frame, alpha=contrast/50, beta=brightness-50)

#         # Menampilkan frame
#         cv2.imshow('Video', frame)

#         # Keluar dari loop jika tombol 'q' ditekan
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Membersihkan resource
#     cap.release()
#     cv2.destroyAllWindows()


# if __name__ == "__main__":
#     main()

import cv2


def nothing(x):
    pass


def main():
    cap = cv2.VideoCapture(0)
    # def make_1080p():
    # cap.set(3, 1920)
    # cap.set(4, 1080)
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

        # Menerapkan CLAHE
        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
        clahe_frame = clahe.apply(gray)

        # Mengubah kembali ke BGR untuk ditampilkan
        clahe_frame = cv2.cvtColor(clahe_frame, cv2.COLOR_GRAY2BGR)

        cv2.imshow('Video', clahe_frame)
        cv2.imshow('Gambar', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
