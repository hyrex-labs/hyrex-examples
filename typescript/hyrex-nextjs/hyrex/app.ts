import { HyrexRegistry } from '@hyrex/hyrex';
import { getHyrexContext } from '@hyrex/hyrex';

export const hy = new HyrexRegistry();

// Define a simple hello world task
const helloWorldTask = hy.task({
    name: 'helloWorld',
    config: {
        queue: 'default',
        timeoutSeconds: 30,
    },
    func: async (input: { name?: string }) => {
        const ctx = getHyrexContext();
        const name = input.name || 'World';

        console.log(`Task ID: ${ctx.taskId}`);
        console.log(`Hello, ${name}! Welcome to Hyrex!`);

        // Simulate some work
        await new Promise(resolve => setTimeout(resolve, 2000));

        return {
            message: `Successfully greeted ${name}`,
            timestamp: new Date().toISOString(),
            taskId: ctx.taskId
        };
    }
});


// Export tasks for easy access
export { helloWorldTask };

// Example usage (uncomment to test):
// if (process.argv.includes('--submit')) {
//     helloWorldTask.send({ name: 'hyrex' });
//     console.log('Task submitted!');
// }
