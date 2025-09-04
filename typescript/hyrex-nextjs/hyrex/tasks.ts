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


// Define a confirmation email task
const sendConfirmationEmailTask = hy.task({
    name: 'sendConfirmationEmail',
    config: {
        queue: 'default',
        timeoutSeconds: 30,
    },
    func: async (input: { email: string }) => {
        const ctx = getHyrexContext();
        const { email } = input;

        console.log(`Task ID: ${ctx.taskId}`);
        console.log(`Sending confirmation email to: ${email}`);

        // Simulate email sending
        await new Promise(resolve => setTimeout(resolve, 1500));

        console.log(`Confirmation email sent successfully to ${email}`);

        return {
            message: `Confirmation email sent to ${email}`,
            timestamp: new Date().toISOString(),
            taskId: ctx.taskId,
            email
        };
    }
});

// Export tasks for easy access
export { helloWorldTask, sendConfirmationEmailTask };

// Example usage (uncomment to test):
// if (process.argv.includes('--submit')) {
//     helloWorldTask.send({ name: 'hyrex' });
//     console.log('Task submitted!');
// }
