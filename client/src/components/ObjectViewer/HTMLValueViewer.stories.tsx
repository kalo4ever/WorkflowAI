import { Meta, StoryObj } from '@storybook/react';
import { HTMLValueViewer } from './HTMLValueViewer';

const meta = {
  title: 'Components/ObjectViewer/HTMLValueViewer',
  component: HTMLValueViewer,
  parameters: {
    layout: 'centered',
  },
  args: {
    keyPath: 'email.body_with_html',
    defs: undefined,
  },
  argTypes: {},
} satisfies Meta<typeof HTMLValueViewer>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Short: Story = {
  args: {
    value: '<h1>Hello, World!</h1>',
  },
};

export const Long: Story = {
  args: {
    value: `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
      />
      <title>Document</title>
    </head>
    <body>
      <h1>Hello, World!</h1>
      <p>
        Lorem ipsum dolor sit amet consectetur adipisicing elit. Quisquam
        quas, quos, voluptates, tempora quae natus doloremque dolores
        voluptatibus doloribus quod repellendus
      </p>
      <img
        src="https://images.pexels.com/photos/1906795/pexels-photo-1906795.jpeg"
        alt="placeholder"
      />
    </body>
    </html>
    `,
  },
};
