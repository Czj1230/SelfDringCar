import os
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from tensorflow.core.protobuf import saver_pb2
import driving_data_pspnet as driving_data
import cnnmodel_sigmoid_2 as cnnmodel
import numpy as np
import matplotlib.pyplot as plt
import time

result = []
LOGDIR = './save/ori_3050_2'

sess = tf.InteractiveSession()

L2NormConst = 0.001

train_vars = tf.trainable_variables()

loss = tf.reduce_mean(tf.square(tf.subtract(cnnmodel.y_, cnnmodel.y))) + tf.add_n([tf.nn.l2_loss(v) for v in train_vars]) * L2NormConst
train_step = tf.train.AdamOptimizer(1e-4).minimize(loss)
sess.run(tf.global_variables_initializer())

# create a summary to monitor cost tensor
tf.summary.scalar("loss", loss)
# merge all summaries into a single op
merged_summary_op = tf.summary.merge_all()

saver = tf.train.Saver(write_version = saver_pb2.SaverDef.V2)

# op to write logs to Tensorboard
logs_path = './logs/ori_3050_2'
summary_writer = tf.summary.FileWriter(logs_path, graph=tf.get_default_graph())

epochs = 30
batch_size = 100

# train over the dataset about 30 times
for epoch in range(epochs):
  for i in range(int(driving_data.num_images/batch_size)):
    xs, ys = driving_data.LoadTrainBatch(batch_size)
    train_step.run(feed_dict={cnnmodel.x: xs, cnnmodel.y_: ys, cnnmodel.keep_prob: 0.8})
    if i % 5 == 0:
      xs, ys = driving_data.LoadValBatch(batch_size)
      loss_value = loss.eval(feed_dict={cnnmodel.x:xs, cnnmodel.y_: ys, cnnmodel.keep_prob: 1.0})
      print("Epoch: %d, Step: %d, Loss: %g" % (epoch, epoch * batch_size + i, loss_value))
      result.append(loss_value)

    # write logs at every iteration
    #summary = merged_summary_op.eval(feed_dict={cnnmodel.x:xs, cnnmodel.y_: ys, cnnmodel.keep_prob: 1.0})
    #summary_writer.add_summary(summary, epoch * driving_data.num_images/batch_size + i)
    
    if i % batch_size == 0:
      if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR)
      checkpoint_path = os.path.join(LOGDIR, "model.ckpt")
      filename = saver.save(sess, checkpoint_path)
  print("Model saved in file: %s" % filename)

print("Run the command line:\n" \
      "--> tensorboard --logdir=./logs " \
      "\nThen open http://0.0.0.0:6006/ into your web browser")
np.save('sigmoid_2', result)
'''
x_axis = [(i + 1) * 5 for i in range(len(result))]
plt.figure()
plt.plot(x_axis, result, label='Sum-of-Square Error Loss for Identify Function')
plt.title('Sum-of-Square Error Loss for CNN Models with Different Activation Functions')
plt.xlabel('step')
plt.ylabel('error loss')
plt.legend()
fig = plt.gcf()
plt.savefig('error_loss_comparison.png')
plt.show()
'''