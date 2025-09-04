import { HyrexApp } from '@hyrex/hyrex';
import { hy as appRegistry } from './tasks';

const hyrexApp = new HyrexApp({
    name: "hyrex"
});

hyrexApp.addRegistry(appRegistry);
hyrexApp.init();
