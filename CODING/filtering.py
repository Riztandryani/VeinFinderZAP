import cv2

# Fungsi untuk menambahkan Gaussian Blur


def apply_gaussian_blur(image):
    return cv2.GaussianBlur(image, (5, 5), 0)


# Inisialisasi webcam
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 180)
cap.set(cv2.CAP_PROP_CONTRAST, 230)

# Buat objek CLAHE
clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))

while True:
    # Baca frame dari kamera
    ret, frame = cap.read()

    # Ubah ke grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Terapkan Gaussian Blur
    blurred = apply_gaussian_blur(gray)

    # Terapkan CLAHE
    clahe_image = clahe.apply(blurred)

    # Tampilkan frame hasil
    cv2.imshow('CLAHE dengan Gaussian Blur', clahe_image)

    # Tunggu tombol 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Tutup webcam dan jendela tampilan
cap.release()
cv2.destroyAllWindows()

# import cv2

# # Fungsi untuk menambahkan Gaussian Blur


# def apply_gaussian_blur(image):
#     return cv2.GaussianBlur(image, (5, 5), 0)

# # Fungsi untuk menambahkan Unsharp Masking


# def apply_unsharp_masking(image):
#     gaussian = cv2.GaussianBlur(image, (9, 9), 10.0)
#     return cv2.addWeighted(image, 1.5, gaussian, -0.5, 0, image)


# # Inisialisasi webcam
# cap = cv2.VideoCapture(1)
# cap.set(cv2.CAP_PROP_BRIGHTNESS, 180)
# cap.set(cv2.CAP_PROP_CONTRAST, 200)

# # Buat objek CLAHE
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# while True:
#     # Baca frame dari kamera
#     ret, frame = cap.read()

#     # Ubah ke grayscale
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # Terapkan Gaussian Blur
#     blurred = apply_gaussian_blur(gray)

#     # Terapkan CLAHE
#     clahe_image = clahe.apply(blurred)

#     # Terapkan Unsharp Masking
#     unsharp_image = apply_unsharp_masking(clahe_image)

#     # Tampilkan frame hasil
#     cv2.imshow('CLAHE dengan Gaussian Blur dan Unsharp Masking', unsharp_image)

#     # Tunggu tombol 'q' untuk keluar
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Tutup webcam dan jendela tampilan
# cap.release()
# cv2.destroyAllWindows()
