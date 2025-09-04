import { HyrexApp } from '@hyrex/hyrex';
import { hy as appRegistry } from './tasks';
import { workflowRegistry } from './workflows';

const hyrexApp = new HyrexApp({
    name: "hyrex"
});

hyrexApp.addRegistry(appRegistry);
hyrexApp.addRegistry(workflowRegistry);
hyrexApp.init();
