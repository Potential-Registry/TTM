import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import unittest
import numpy as np
from TTM import load_potential


class PotentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=json.loads(Path(__file__).with_name('reference.json').read_text())
        cls.pes=load_potential(os.environ.get('POTENTIAL_LIBRARY'))

    def evaluate(self,record,coords=None,gradient=True):
        args={'coords':np.array(record['coords']) if coords is None else coords}
        args['imodel']=record['imodel']
        return (self.pes.get_pot_grad if gradient else self.pes.get_pot)(**args)

    def test_00_concurrent_first_calls(self):
        barrier=threading.Barrier(8)
        def call(i):
            barrier.wait(timeout=30)
            record=self.records[i*4 % len(self.records)]
            return record,self.evaluate(record)
        cwd=os.getcwd()
        with ThreadPoolExecutor(max_workers=8) as pool:
            for record,result in pool.map(call,range(8)):
                np.testing.assert_allclose(result['energy'],record['energy'],rtol=1e-10,atol=1e-11)
                np.testing.assert_allclose(result['grad'],record['grad'],rtol=1e-9,atol=1e-10)
        self.assertEqual(cwd,os.getcwd())

    def test_original_serial_reference(self):
        for record in self.records:
            result=self.evaluate(record)
            np.testing.assert_allclose(result['energy'],record['energy'],rtol=1e-10,atol=1e-11)
            np.testing.assert_allclose(result['grad'],record['grad'],rtol=1e-9,atol=1e-10)
            self.assertEqual(result['energy'],self.evaluate(record,gradient=False))

    def test_thread_stress(self):
        expected=[self.evaluate(r) for r in self.records]
        def call(i):
            index=i % len(self.records)
            result=self.evaluate(self.records[index])
            np.testing.assert_array_equal(result['energy'],expected[index]['energy'])
            np.testing.assert_array_equal(result['grad'],expected[index]['grad'])
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(call,range(2048)))

    def test_batch_layout_and_buffers(self):
        record=self.records[0]
        x=np.array(record['coords'])
        batch=np.array([x,x,x,x]).reshape(2,2,*x.shape)
        original=batch.copy()
        result=self.evaluate(record,coords=batch)
        self.assertEqual(result['energy'].shape,(2,2))
        self.assertEqual(result['grad'].shape,batch.shape)
        np.testing.assert_array_equal(result['energy'],np.full((2,2),self.evaluate(record,coords=x,gradient=False)))
        np.testing.assert_allclose(result['grad'],np.broadcast_to(record['grad'],batch.shape),rtol=1e-9,atol=1e-10)
        strided=self.evaluate(record,coords=batch[::-1,::-1])
        np.testing.assert_array_equal(strided['grad'],result['grad'])
        again=self.evaluate(record,coords=batch)
        self.assertFalse(np.shares_memory(result['grad'],again['grad']))
        np.testing.assert_array_equal(batch,original)
        empty=self.evaluate(record,coords=np.empty((0,*x.shape)))
        self.assertEqual(empty['energy'].shape,(0,))

    def test_gradient_finite_difference(self):
        record=next(r for r in self.records if len(r['coords'])==6)
        x=np.array(record['coords']); result=self.evaluate(record)
        step=1e-5
        for atom,axis in [(0,0),(2,1),(4,2)]:
            plus=x.copy();minus=x.copy()
            plus[atom,axis]+=step;minus[atom,axis]-=step
            derivative=(self.evaluate(record,plus,False)-self.evaluate(record,minus,False))/(2*step)
            self.assertAlmostEqual(derivative,result['grad'][atom,axis],delta=2e-7)

    def test_input_validation(self):
        for coords in [np.zeros((3,3)),np.full((3,3),np.nan),np.zeros((4,3)),np.zeros(9)]:
            with self.assertRaises(ValueError):
                self.pes.get_pot(coords=coords)
        with self.assertRaises(ValueError):
            self.pes.get_pot(coords=np.array(self.records[0]['coords']),nwaters=100)


if __name__=='__main__':
    unittest.main()
