mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE="../cmake/arm.toolchain.cmake" \
    -DTHREADS_PTHREAD_ARG="-pthread" \
    -DNO_BOOT=ON \
    -DENABLE_SSE42=OFF \
	-DENABLE_PYTHON=ON \
	-DPYTHON_EXECUTABLE=/usr/bin/python3.7 \
	-DPYTHON_LIBRARY=/usr/lib/arm-linux-gnueabihf/libpython3.7m.so \
	-DPYTHON_INCLUDE_DIR=/usr/include/python3.7 \
    -DTHREADING=SEQ \
    -DENABLE_GNA=OFF .. && make --jobs=$(nproc --all)