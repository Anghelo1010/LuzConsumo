-- Eliminar la tabla existente si existe
DROP TABLE IF EXISTS fibonacci_cos;

-- Crear la base de datos
CREATE DATABASE fibonacci_trigonometric;
USE fibonacci_trigonometric;

-- Crear la tabla
CREATE TABLE fibonacci_cos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    tipo_serie VARCHAR(50),
    resultado FLOAT,
    cos_fib FLOAT,
    error FLOAT,
    iteraciones INT,
    fecha DATETIME
);

-- Datos de prueba
INSERT INTO fibonacci_cos (usuario_id, tipo_serie, resultado, cos_fib, error, iteraciones, fecha) VALUES
(1, 'Fibonacci', 0.0, 1.0, 0.0, 1, '2025-03-15 10:00:00'),
(1, 'Fibonacci', 1.0, 0.540302, 0.040302, 2, '2025-03-15 10:01:00'),
(1, 'Fibonacci', 1.0, 0.540302, 0.040302, 3, '2025-03-15 10:02:00'),
(2, 'Fibonacci', 2.0, -0.416147, 0.749480, 4, '2025-03-15 10:03:00'),
(2, 'Fibonacci', 3.0, -0.989992, 0.739998, 5, '2025-03-15 10:04:00'),
(2, 'Fibonacci', 5.0, 0.283662, 0.711887, 6, '2025-03-15 10:05:00');