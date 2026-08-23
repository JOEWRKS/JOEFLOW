import path from 'node:path';

const sourceRoot = process.env.JOEWRKS_FROZEN_SOURCE_ROOT;
if (!sourceRoot) throw new Error('JOEWRKS_FROZEN_SOURCE_ROOT is required');

export default {
  resolve: {
    alias: [
      { find: '@frozen-b-engine', replacement: path.join(sourceRoot, 'src/domain/engine.ts') },
      { find: '@frozen-b-seed', replacement: path.join(sourceRoot, 'src/domain/seed.ts') },
      { find: '@frozen-b-selectors', replacement: path.join(sourceRoot, 'src/domain/selectors.ts') },
    ],
  },
  test: {
    globals: true,
    environment: 'node',
    include: ['vitest_b_adapter.test.ts'],
    maxWorkers: 1,
    minWorkers: 1,
  },
};
