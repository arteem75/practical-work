import java.util.stream.*;
import java.util.function.*;
import java.awt.*;

class Main {
    public static class Spectrum {
        public double[] getEnergy() {
            return new double[0];
        }
    }

    protected Spectrum spectrum;

    public static class Ref<T> {
        T value;

        public Ref() {
        }

        public Ref(T value) {
            this.value = value;
        }

        public boolean isNull() {
            return value == null;
        }

        public T get() {
            return value;
        }

        public void set(T value) {
            this.value = value;
        }
    }

    public static <T>T maxKey(Stream<T> stream, Function<T, Double> function) {
        Ref<Double> max = new Ref<>();
        Ref<T> index = new Ref<>();
        stream.forEach(v -> {
		Double value = function.apply(v);

		if (max.isNull() || value > max.get()) {
		    max.set(value);
		    index.set(v);
		}
	    });

        return index.get();
    }

    public static int interpolate(int x, int x0, int x1, int y0, int y1) {
        return y0 + (x - x0) * (y1 - y0) / (x1 - x0);
    }

    public static double interpolate(double x, double x0, double x1, double y0, double y1) {
        return y0 + (x - x0) * (y1 - y0) / (x1 - x0);
    }

    protected int getXByFrequency(double frequency) {
        Insets insets = null;
        return (int) Math.round(interpolate(frequency, getMinSpectrumCoord(), getMaxSpectrumCoord(), insets.left, getWidth() - insets.right));
    }

    private int getWidth() {
        return 0;
    }

    private double getMaxSpectrumCoord() {
        return 0;
    }

    private double getMinSpectrumCoord() {
        return 0;
    }

    void foo() {
        int maxBpmIndex = 0;
        int xcur = getXByFrequency(maxKey(IntStream.range(0, maxBpmIndex).boxed(), i -> Math.abs(spectrum.getEnergy()[i])));
    }
}
