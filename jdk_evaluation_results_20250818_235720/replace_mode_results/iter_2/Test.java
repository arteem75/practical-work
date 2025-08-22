/**
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.locks.ReentrantLock;

public class Test {
    private static final FlusherPool FLUSHER = new FlusherPool();

    private static class FlusherPool { 
        private Timer _timer = new Timer("disruptor-flush-trigger", true);
        private ThreadPoolExecutor _exec = new ThreadPoolExecutor(1, 100, 10, TimeUnit.SECONDS, new ArrayBlockingQueue<Runnable>(1024), new ThreadPoolExecutor.DiscardPolicy());
        private HashMap<Long, ArrayList<Flusher>> _pendingFlush = new HashMap<>();
        private HashMap<Long, TimerTask> _tt = new HashMap<>();

        public synchronized void start(Flusher flusher, final long flushInterval) {
            ArrayList<Flusher> pending = _pendingFlush.get(flushInterval);
            if (pending == null) {
                pending = new ArrayList<>();
                TimerTask t = new TimerTask() {
                    @Override
                    public void run() {
                        invokeAll(flushInterval);
                    }
                };
                _pendingFlush.put(flushInterval, pending);
                _timer.schedule(t, flushInterval, flushInterval);
                _tt.put(flushInterval, t);
            }
            pending.add(flusher);
        }

        private synchronized void invokeAll(int flushInterval) {
            ArrayList<Flusher> tasks = _pendingFlush.get(flushInterval);
            if (tasks != null) {
                for (Flusher f: tasks) {
                    _exec.submit(f);
                }
            }
        }

        public synchronized void stop(Flusher flusher, long flushInterval) {
            ArrayList<Flusher> pending = _pendingFlush.get(flushInterval);
            pending.remove(flusher);
            if (pending.size() == 0) {
                _pendingFlush.remove(flushInterval);
                _tt.remove(flushInterval).cancel();
            }
        }
    }

    private class Flusher implements Runnable {
        public void run() {
            //NOOP
        }
    }
}